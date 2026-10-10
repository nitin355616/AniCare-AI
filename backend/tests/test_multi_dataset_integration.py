"""
AniCare AI — Automated Tests for Multi-Dataset Integration & Real Models
Tests Dataset Explorer endpoints, Model Metrics, PyTorch Real Inference,
Species Guard Classifier, and Muzzle Biometric Registry.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_dataset_info_endpoint():
    """Verify /api/datasets/info returns valid multi-dataset audit metadata."""
    response = client.get("/api/datasets/info")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    summary = data["summary"]
    assert "datasets" in summary
    assert len(summary["datasets"]) == 5
    assert "tasks" in summary
    assert summary["tasks"]["task_a_cattle_disease"]["total_images"] >= 3600


def test_dataset_gallery_pagination():
    """Verify /api/datasets/gallery returns paginated items with labels and urls."""
    response = client.get("/api/datasets/gallery?page=1&page_size=12")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["page"] == 1
    assert data["page_size"] == 12
    assert len(data["items"]) == 12
    first = data["items"][0]
    assert "id" in first
    assert "class_label" in first
    assert "image_url" in first


def test_dataset_gallery_filter_by_class():
    """Verify /api/datasets/gallery filters correctly by class_label."""
    response = client.get("/api/datasets/gallery?class_label=Foot and Mouth Disease&page=1&page_size=6")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    for item in data["items"]:
        assert item["class_label"] == "Foot and Mouth Disease"


def test_dataset_image_streaming():
    """Verify /api/datasets/image/{id} securely streams image bytes."""
    response = client.get("/api/datasets/image/disease_00200")
    assert response.status_code == 200
    assert response.headers["content-type"] in ["image/jpeg", "image/png"]
    assert len(response.content) > 1000


def test_models_status_endpoint():
    """Verify /api/models/status returns operational status for trained models."""
    response = client.get("/api/models/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    models = data["models"]
    assert "task_a_disease" in models
    assert "task_b_species" in models
    assert "task_c_muzzle" in models
    assert models["task_a_disease"]["status"] == "READY"
    assert models["task_b_species"]["status"] == "READY"
    assert models["task_c_muzzle"]["status"] == "INDEXED"


def test_models_metrics_endpoint():
    """Verify /api/models/metrics returns held-out test evaluation benchmarks."""
    response = client.get("/api/models/metrics")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    disease_m = data["metrics"]["task_a_disease"]
    assert disease_m["test_metrics"]["accuracy"] > 0.90
    assert "confusion_matrix" in disease_m["test_metrics"]
    assert len(disease_m["test_metrics"]["confusion_matrix"]) == 3


def test_real_disease_prediction_endpoint():
    """Verify /api/detection/predict-real runs genuine PyTorch inference on sample."""
    response = client.post("/api/detection/predict-real", json={"image_id": "disease_00200"})
    assert response.status_code == 200
    res = response.json()
    assert res["is_real_inference"] is True
    assert res["is_demo_inference"] is False
    assert res["possible_condition"] == "Foot and Mouth Disease"
    assert res["confidence"] > 0.90
    assert res["risk_level"] in ["CRITICAL", "HIGH"]
    assert "probabilities" in res
    assert "differential_diagnoses" in res


def test_species_guard_prediction_endpoint():
    """Verify /api/detection/validate-species runs Task B species guard."""
    response = client.post("/api/detection/validate-species", json={"image_id": "species_00304"})
    assert response.status_code == 200
    res = response.json()
    assert "predicted_species" in res
    assert res["predicted_species"] == "Cattle"
    assert res["is_bovine"] is True
    assert res["confidence"] > 0.80


def test_muzzle_registry_endpoint():
    """Verify /api/detection/muzzle-registry returns registered animal profiles."""
    response = client.get("/api/detection/muzzle-registry")
    assert response.status_code == 200
    reg = response.json()
    assert "total_registered_animals" in reg
    assert reg["total_registered_animals"] >= 70
    assert "animals" in reg


def test_real_disease_missing_image_id():
    """Verify 400 Bad Request when image_id is omitted."""
    response = client.post("/api/detection/predict-real", json={})
    assert response.status_code == 400
    assert "Missing image_id" in response.json()["detail"]


def test_real_disease_nonexistent_image_id():
    """Verify 404 Not Found when image does not exist."""
    response = client.post("/api/detection/predict-real", json={"image_id": "nonexistent_img_99999"})
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_real_disease_path_traversal_attempt():
    """Verify path traversal attempt is safely rejected."""
    response = client.post("/api/detection/predict-real", json={"image_id": "../../../../windows/win.ini"})
    assert response.status_code == 404


def test_upload_and_predict_real_end_to_end():
    """Verify end-to-end synthetic image upload, storage, and genuine neural prediction."""
    import io
    from PIL import Image

    # Create synthetic test fixture image for API pipeline verification
    img = Image.new("RGB", (224, 224), color=(128, 100, 80))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)

    # 1. Upload photo
    upload_resp = client.post(
        "/api/detection/upload",
        files={"file": ("synthetic_test.jpg", buf, "image/jpeg")}
    )
    assert upload_resp.status_code == 201
    upload_data = upload_resp.json()
    assert "image_id" in upload_data
    uploaded_id = upload_data["image_id"]

    # 2. Run real prediction on uploaded image
    pred_resp = client.post(
        "/api/detection/predict-real",
        json={"image_id": uploaded_id}
    )
    assert pred_resp.status_code == 200
    pred = pred_resp.json()
    assert pred["is_real_inference"] is True
    assert pred["is_demo_inference"] is False
    assert pred["possible_condition"] in ["Healthy / Normal", "Foot and Mouth Disease", "Lumpy Skin Disease"]
    assert 0.0 <= pred["confidence"] <= 1.0
    assert pred["risk_level"] in ["LOW", "HIGH", "CRITICAL"]
    assert "probabilities" in pred
    assert len(pred["probabilities"]) == 3
    assert "recommended_immediate_actions" in pred
    assert len(pred["recommended_immediate_actions"]) > 0
    assert "disclaimer" in pred
    assert "veterinarian" in pred["disclaimer"].lower()


def test_predict_real_corrupted_image_handling(tmp_path):
    """Verify unreadable image triggers a 400 Bad Request error cleanly without 500 crash."""
    import io
    # Construct file with JPEG magic bytes followed by truncated/garbage bytes
    garbage_bytes = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00corrupted_non_image_payload"
    buf = io.BytesIO(garbage_bytes)

    upload_resp = client.post(
        "/api/detection/upload",
        files={"file": ("corrupt_test.jpg", buf, "image/jpeg")}
    )
    assert upload_resp.status_code == 201
    corrupt_id = upload_resp.json()["image_id"]

    pred_resp = client.post(
        "/api/detection/predict-real",
        json={"image_id": corrupt_id}
    )
    assert pred_resp.status_code == 400
    assert "invalid or unreadable" in pred_resp.json()["detail"].lower()

