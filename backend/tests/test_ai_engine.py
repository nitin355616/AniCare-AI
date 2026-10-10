import io
import pytest
from pathlib import Path
from PIL import Image

from backend.ai.inference.demo_engine import demo_inference_engine
from backend.ai.inference.vision_engine import (
    RealVisionInferenceEngine,
    vision_inference_engine,
    get_inference_engine
)
from backend.ai.postprocessing.risk_engine import clinical_risk_engine
from backend.ai.preprocessing.image_preprocessor import image_preprocessor
from backend.ai.config import ai_config
from app.schemas.detection import DetectionAnalyzeRequest

@pytest.mark.asyncio
async def test_demo_engine_fallback():
    """1. Test DemoInferenceEngine returns structured assessment with demo flags."""
    req = DetectionAnalyzeRequest(
        species="Cattle",
        temperature="101.8 °F",
        appetite="Normal",
        symptoms=["Slight nasal discharge"]
    )
    result = await demo_inference_engine.infer(req)

    assert result["is_demo_inference"] is True
    assert result["model_version"] == ai_config.DEMO_MODEL_VERSION
    assert result["veterinary_review_required"] is True
    assert "possible_condition" in result
    assert "confidence" in result
    assert "risk_level" in result
    assert isinstance(result["symptoms_detected"], list)

@pytest.mark.asyncio
async def test_vision_engine_unavailable_fallback():
    """2. Test RealVisionInferenceEngine gracefully delegates to Demo when weights are absent."""
    # Instance with non-existent dummy weights path
    dummy_engine = RealVisionInferenceEngine(
        onnx_weights_path=Path("non_existent_weights.onnx"),
        torch_weights_path=Path("non_existent_weights.pt")
    )

    assert dummy_engine.has_weights() is False
    assert dummy_engine.is_available() is False

    meta = dummy_engine.get_model_metadata()
    assert meta["status"] == "weights_pending_fallback_active"
    assert meta["weights_present"] is False

    # Calling infer must not crash; it safely falls back to Demo engine
    req = DetectionAnalyzeRequest(
        species="Buffalo",
        temperature="104.9 °F",
        symptoms=["Excessive salivation", "Vesicles on tongue"]
    )
    result = await dummy_engine.infer(req)
    assert result is not None
    assert "Foot and Mouth Disease" in result["possible_condition"]
    assert result["risk_level"] == "CRITICAL"
    assert result["is_demo_inference"] is True

def test_risk_engine_decoupling_and_severity():
    """3. Test Risk Engine decouples model confidence from pathological risk."""
    # Case A: High confidence (99%) on mild condition -> must evaluate to LOW or MODERATE risk
    mild_eval = clinical_risk_engine.evaluate_risk(
        condition_name="Superficial Ringworm (Dermatophytosis)",
        confidence=99.2,
        species="Cattle",
        temperature="101.2 °F",
        appetite="Normal",
        activity_level="Active",
        breathing_condition="Normal"
    )
    assert mild_eval["risk_level"] in ["LOW", "MODERATE"]
    assert mild_eval["risk_score"] < 50.0

    # Case B: Epizootic transboundary condition (FMD) -> must escalate to CRITICAL
    fmd_eval = clinical_risk_engine.evaluate_risk(
        condition_name="Foot and Mouth Disease",
        confidence=75.0,  # Even with moderate confidence, biosecurity precautionary tier applies!
        species="Cattle",
        temperature="105.2 °F",
        symptoms=["Ropy salivation", "Mucosal vesicles"],
        breathing_condition="Labored",
        activity_level="Recumbent"
    )
    assert fmd_eval["risk_level"] == "CRITICAL"
    assert fmd_eval["risk_score"] >= 80.0
    assert fmd_eval["urgency"] == "IMMEDIATE_QUARANTINE"
    assert len(fmd_eval["contributing_factors"]) >= 2

def test_api_response_compatibility(client):
    """4. Test /api/detection/analyze maintains strict backward compatibility and adds explainability."""
    payload = {
        "species": "Cattle",
        "temperature": "104.8 °F",
        "appetite": "Severely Reduced",
        "activity_level": "Lethargic",
        "breathing_condition": "Rapid and labored",
        "symptoms": ["Dyspneic breathing", "Serous discharge", "Core pyrexia"],
        "observations": "Grunting sounds during expiration."
    }

    res = client.post("/api/detection/analyze", json=payload)
    assert res.status_code == 200, res.text
    data = res.json()

    # Core required contract fields
    assert "possible_condition" in data
    assert "confidence" in data
    assert "risk_level" in data
    assert "symptoms_detected" in data
    assert "explanation" in data
    assert "recommended_immediate_actions" in data
    assert data["veterinary_review_required"] is True

    # New explainability fields
    assert "symptom_evidence" in data
    assert "detected_visual_indicators" in data
    assert "contributing_factors" in data
    assert "risk_reasoning" in data
    assert "risk_score" in data

def test_invalid_image_handling(tmp_path):
    """5. Test ImagePreprocessor rejects non-existent, invalid format, and corrupted files."""
    # Non-existent file
    with pytest.raises(FileNotFoundError):
        image_preprocessor.validate_image_file("non_existent_image.jpg")

    # Invalid extension
    script_file = tmp_path / "malicious.exe"
    script_file.write_bytes(b"MZ\x90\x00")
    with pytest.raises(ValueError) as exc:
        image_preprocessor.validate_image_file(str(script_file))
    assert "Unsupported image extension" in str(exc.value)

    # Valid image creates tensor of shape (1, 3, 224, 224)
    valid_img = tmp_path / "cow_sample.jpg"
    img = Image.new("RGB", (320, 240), color=(120, 80, 40))
    img.save(valid_img, format="JPEG")

    tensor, meta = image_preprocessor.preprocess(str(valid_img))
    assert tensor.shape == (1, 3, 224, 224)
    assert meta["channels"] == 3
    assert meta["original_width"] == 320

def test_model_metadata():
    """6. Test model metadata structures for both Vision and Demo engines."""
    demo_meta = demo_inference_engine.get_model_metadata()
    assert demo_meta["engine"] == "DemoInferenceEngine"
    assert demo_meta["is_demo_inference"] is True

    vision_meta = vision_inference_engine.get_model_metadata()
    assert vision_meta["engine"] == "RealVisionInferenceEngine"
    assert any(arch in vision_meta["architecture"].lower() for arch in ["efficientnet", "mobilenet"])
    assert vision_meta["weights_present"] is True

    # Factory now resolves to RealVisionInferenceEngine because weights are deployed
    selected_engine = get_inference_engine(prefer_vision=True)
    assert selected_engine.is_available() is True
    assert selected_engine.__class__.__name__ == "RealVisionInferenceEngine"

def test_safety_flags_and_disclaimer(client):
    """7. Test veterinary safety flags and mandatory disclaimer."""
    payload = {
        "species": "Goat",
        "temperature": "102.0 °F",
        "symptoms": ["Mild cough"]
    }
    res = client.post("/api/detection/analyze", json=payload)
    assert res.status_code == 200
    data = res.json()

    # Safety assertions
    assert data["veterinary_review_required"] is True
    assert data["is_demo_inference"] is True
    assert "disclaimer" in data
    assert "does not issue medical prescriptions" in data["disclaimer"].lower()
