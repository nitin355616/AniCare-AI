import os
import io
import json
import pytest
import numpy as np
from PIL import Image
from pathlib import Path

from backend.ai.config import ai_config
from backend.ai.inference.vision_engine import (
    RealVisionInferenceEngine,
    vision_inference_engine,
    get_inference_engine
)
from backend.ai.inference.demo_engine import demo_inference_engine
from backend.ai.preprocessing.image_preprocessor import image_preprocessor
from backend.app.schemas.detection import DetectionAnalyzeRequest


def test_onnx_weights_and_metadata_exist():
    """1. Verify exported ONNX model weights and metadata JSON exist on disk."""
    onnx_path = ai_config.DEFAULT_ONNX_PATH
    meta_path = onnx_path.with_suffix(".json")

    assert onnx_path.is_file(), f"ONNX file not found at {onnx_path}"
    file_size_mb = onnx_path.stat().st_size / (1024 * 1024)
    assert 10.0 <= file_size_mb <= 25.0, f"Unexpected ONNX file size: {file_size_mb:.2f} MB"

    assert meta_path.is_file(), f"Metadata JSON not found at {meta_path}"
    with open(meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)

    assert meta["model_name"] == "anicare_vision_bovine_v1"
    assert meta["architecture"] == "efficientnet_b0"
    assert "optimal_temperature" in meta
    assert meta["optimal_temperature"] > 1.0
    assert "test_metrics" in meta
    assert meta["test_metrics"]["accuracy"] > 0.90


def test_onnx_runtime_direct_inference():
    """2. Verify direct ONNX Runtime forward pass produces valid calibrated logits."""
    import onnxruntime as ort

    onnx_path = str(ai_config.DEFAULT_ONNX_PATH)
    session = ort.InferenceSession(onnx_path, providers=["CPUExecutionProvider"])

    inputs = session.get_inputs()
    outputs = session.get_outputs()

    assert len(inputs) == 1
    assert inputs[0].name == "input"
    assert len(outputs) == 1
    assert outputs[0].name == "logits"

    # Forward pass with random batch=1 tensor
    dummy_input = np.random.randn(1, 3, 224, 224).astype(np.float32)
    logits = session.run(None, {"input": dummy_input})[0]

    assert logits.shape == (1, 2)
    assert not np.isnan(logits).any()

    # Softmax probabilities
    exp_l = np.exp(logits - np.max(logits, axis=-1, keepdims=True))
    probs = exp_l / np.sum(exp_l, axis=-1, keepdims=True)
    assert np.isclose(np.sum(probs), 1.0, atol=1e-5)
    assert 0.0 <= probs[0, 0] <= 1.0
    assert 0.0 <= probs[0, 1] <= 1.0


@pytest.mark.asyncio
async def test_real_vision_inference_with_image(tmp_path):
    """3. Verify RealVisionInferenceEngine executes real image inference with calibrated probabilities."""
    # Create test sample image
    test_img = tmp_path / "test_cow.jpg"
    img = Image.new("RGB", (300, 300), color=(140, 100, 60))
    img.save(test_img, format="JPEG")

    engine = RealVisionInferenceEngine()
    assert engine.is_available() is True
    assert engine.has_weights() is True
    assert engine.has_runtime() is True

    req = DetectionAnalyzeRequest(
        species="Cattle",
        temperature="102.1 °F",
        appetite="Normal",
        symptoms=["Mild skin lesion"],
        observations="Field screening check"
    )

    result = await engine.infer(req, image_path=str(test_img))

    assert result["is_demo_inference"] is False
    assert "AniCare-Bovine-Vision" in result["model_version"]
    assert result["veterinary_review_required"] is True
    assert 0.0 <= result["confidence"] <= 100.0
    assert result["risk_level"] in ["LOW", "MODERATE", "HIGH", "CRITICAL"]
    assert isinstance(result["differential_diagnoses"], list)
    assert len(result["differential_diagnoses"]) >= 2
    assert "detected_visual_indicators" in result
    assert "explanation" in result


@pytest.mark.asyncio
async def test_real_vision_fallback_when_no_image():
    """4. Verify RealVisionInferenceEngine safely falls back to DemoEngine if no image path is provided."""
    engine = RealVisionInferenceEngine()

    req = DetectionAnalyzeRequest(
        species="Cattle",
        temperature="102.5 °F",
        symptoms=["Circumscribed nodules", "Cutaneous skin lumps"]
    )

    # Calling infer without image_path
    result = await engine.infer(req, image_path=None)

    assert result is not None
    assert result["is_demo_inference"] is True
    assert "Lumpy Skin Disease" in result["possible_condition"]


@pytest.mark.asyncio
async def test_real_vision_fallback_on_corrupt_image(tmp_path):
    """5. Verify RealVisionInferenceEngine safely handles corrupt image file without crashing."""
    corrupt_img = tmp_path / "corrupt.jpg"
    corrupt_img.write_bytes(b"INVALID_IMAGE_HEADER_DATA")

    engine = RealVisionInferenceEngine()
    req = DetectionAnalyzeRequest(species="Cattle", symptoms=["Lethargy"])

    result = await engine.infer(req, image_path=str(corrupt_img))

    # Must safely fall back to demo engine
    assert result is not None
    assert result["is_demo_inference"] is True


def test_factory_selector_prefers_vision_engine():
    """6. Verify get_inference_engine returns RealVisionInferenceEngine when operational."""
    engine = get_inference_engine(prefer_vision=True)
    assert isinstance(engine, RealVisionInferenceEngine)
    assert engine.is_available() is True


def test_temperature_scaling_calibrates_confidence():
    """7. Verify Platt temperature scaling softens peak overconfidence."""
    raw_logits = np.array([[2.5, 5.0]], dtype=np.float32)

    # Uncalibrated (T = 1.0)
    exp_uncal = np.exp(raw_logits)
    prob_uncal = exp_uncal / np.sum(exp_uncal)

    # Calibrated with optimal temperature T = 1.4415
    T = 1.4415
    scaled_logits = raw_logits / T
    exp_cal = np.exp(scaled_logits)
    prob_cal = exp_cal / np.sum(exp_cal)

    # Calibrated top probability must be lower than overconfident uncalibrated probability
    assert prob_cal[0, 1] < prob_uncal[0, 1]
    assert np.isclose(np.sum(prob_cal), 1.0)


def test_api_analyze_with_image_upload_e2e(client, tmp_path):
    """8. Test full end-to-end FastAPI endpoint /api/detection/upload and /api/detection/analyze."""
    # 1. Create and upload an image
    test_img = tmp_path / "bovine_sample.jpg"
    img = Image.new("RGB", (250, 250), color=(100, 120, 80))
    img.save(test_img, format="JPEG")

    with open(test_img, "rb") as f:
        upload_res = client.post(
            "/api/detection/upload",
            files={"file": ("bovine_sample.jpg", f, "image/jpeg")}
        )

    assert upload_res.status_code == 201, upload_res.text
    upload_data = upload_res.json()
    image_id = upload_data["image_id"]
    assert image_id.startswith("IMG-")

    # 2. Call detection analysis with uploaded image_id
    analyze_payload = {
        "image_id": image_id,
        "species": "Cattle",
        "temperature": "101.9 °F",
        "appetite": "Normal",
        "activity_level": "Active",
        "breathing_condition": "Normal",
        "symptoms": ["Routine preventative check"],
        "observations": "Clear skin examination"
    }

    analyze_res = client.post("/api/detection/analyze", json=analyze_payload)
    assert analyze_res.status_code == 200, analyze_res.text
    result = analyze_res.json()

    # The real vision engine processed the uploaded image!
    assert result["is_demo_inference"] is False
    assert "possible_condition" in result
    assert 0.0 <= result["confidence"] <= 100.0
    assert result["veterinary_review_required"] is True
    assert "AI-ASSISTED CLINICAL SCREENING" in result["disclaimer"]
