import io
import uuid
import pytest

def test_root_discovery(client):
    """Test root service discovery endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "AniCare AI" in data["service"]
    assert data["status"] == "operational"

def test_health_check(client):
    """Test health check returns backend and database connectivity."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "database" in data
    assert data["database"]["connected"] is True
    assert "latency_ms" in data["database"]

def test_auth_workflow(client):
    """Test user registration, login, and profile lookup with JWT."""
    unique_suffix = uuid.uuid4().hex[:6]
    test_email = f"vet_{unique_suffix}@anicare.ai"
    test_password = "SecurePassword@2026"

    # 1. Register
    reg_payload = {
        "email": test_email,
        "username": f"dr_{unique_suffix}",
        "full_name": "Dr. Test Veterinarian",
        "password": test_password,
        "role": "veterinarian",
        "license_number": f"VET-LIC-{unique_suffix.upper()}",
        "phone": "+91 98765 43210"
    }
    reg_res = client.post("/api/auth/register", json=reg_payload)
    assert reg_res.status_code == 201, reg_res.text
    token_resp = reg_res.json()
    assert "access_token" in token_resp
    assert token_resp["user"]["email"] == test_email
    assert token_resp["user"]["role"] == "veterinarian"

    # 2. Login
    login_payload = {
        "email": test_email,
        "password": test_password
    }
    login_res = client.post("/api/auth/login", json=login_payload)
    assert login_res.status_code == 200, login_res.text
    token_data = login_res.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"
    token = token_data["access_token"]

    # 3. Access /api/auth/me
    me_res = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert me_res.status_code == 200
    profile = me_res.json()
    assert profile["email"] == test_email
    assert profile["full_name"] == "Dr. Test Veterinarian"

def test_animals_crud(client):
    """Test livestock registry CRUD operations."""
    # 1. List animals (pre-seeded)
    list_res = client.get("/api/animals")
    assert list_res.status_code == 200
    animals_data = list_res.json()
    assert "items" in animals_data
    assert animals_data["total"] >= 1

    # 2. Create new animal
    tag_id = f"TAG-TST-{uuid.uuid4().hex[:4].upper()}"
    create_payload = {
        "name": "Bhim",
        "tag": tag_id,
        "species": "Buffalo",
        "breed": "Murrah",
        "gender": "Male",
        "age": "3.5 years",
        "weight": "540 kg",
        "location": "Shed 09 - Testing Bay",
        "owner": "National Dairy Research Institute",
        "health_status": "Healthy",
        "risk_level": "Low Risk",
        "symptoms": []
    }
    create_res = client.post("/api/animals", json=create_payload)
    assert create_res.status_code == 201, create_res.text
    created = create_res.json()
    animal_id = created["animal_id"]
    assert created["tag"] == tag_id
    assert created["name"] == "Bhim"

    # 3. Get animal by ID
    get_res = client.get(f"/api/animals/{animal_id}")
    assert get_res.status_code == 200
    assert get_res.json()["animal_id"] == animal_id

    # 4. Update animal
    update_res = client.put(f"/api/animals/{animal_id}", json={
        "health_status": "Under Observation",
        "weight": "548 kg",
        "symptoms": ["Mild lethargy"]
    })
    assert update_res.status_code == 200
    assert update_res.json()["health_status"] == "Under Observation"
    assert update_res.json()["weight"] == "548 kg"

    # 5. Delete animal
    del_res = client.delete(f"/api/animals/{animal_id}")
    assert del_res.status_code == 200
    assert del_res.json()["success"] is True

def test_health_records(client):
    """Test health telemetry logging and historical retrieval."""
    animal_id = "AN-GJ-2024-0104"
    record_payload = {
        "animal_id": animal_id,
        "temperature": "104.2 °F",
        "appetite": "Reduced by 50%",
        "activity": "Lethargic",
        "breathing": "Rapid and labored",
        "symptoms": ["Oral lesions", "Salivation"],
        "observations": "Telemetry spike recorded by smart ear tag #8821.",
        "previous_conditions": ["None reported"],
        "vaccination_status": "FMD dose 1 administered (2025)",
        "recorded_by": "Field Technician - Ramesh"
    }

    create_res = client.post("/api/health-records", json=record_payload)
    assert create_res.status_code == 201, create_res.text
    record_data = create_res.json()
    assert record_data["animal_id"] == animal_id
    assert "id" in record_data

    # Retrieve history
    history_res = client.get(f"/api/animals/{animal_id}/health-records")
    assert history_res.status_code == 200
    history = history_res.json()
    assert history["total"] >= 1
    assert any(r["animal_id"] == animal_id for r in history["records"])

def test_detection_photo_upload_and_validation(client):
    """Test safe photo upload with header validation and non-executable storage."""
    # Valid PNG header (8-byte PNG magic header + dummy bytes)
    valid_png_content = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4"
    file_tuple = ("test_image.png", io.BytesIO(valid_png_content), "image/png")

    upload_res = client.post(
        "/api/detection/upload",
        files={"file": file_tuple}
    )
    assert upload_res.status_code == 201, upload_res.text
    upload_data = upload_res.json()
    assert "image_id" in upload_data
    assert upload_data["image_id"].startswith("IMG-")
    assert upload_data["content_type"] == "image/png"
    assert upload_data["url"].startswith("/uploads/")

    # Invalid file (e.g., text file disguised as image)
    fake_file = ("script.png", io.BytesIO(b"echo 'malicious script'"), "image/png")
    invalid_res = client.post(
        "/api/detection/upload",
        files={"file": fake_file}
    )
    assert invalid_res.status_code == 400
    assert "signature does not match" in invalid_res.text

def test_disease_detection_analysis(client):
    """Test AI Demo Inference Engine with multivariable inputs."""
    # Test Respiratory Infection pattern
    payload_resp = {
        "species": "Cattle",
        "temperature": "103.8 °F",
        "appetite": "Depressed",
        "activity_level": "Lethargic",
        "breathing_condition": "Rapid and shallow",
        "symptoms": ["Rapid dyspneic breathing", "Serous nasal discharge", "Pyrexia"],
        "observations": "Audible grunting during expiration."
    }
    res = client.post("/api/detection/analyze", json=payload_resp)
    assert res.status_code == 200, res.text
    analysis = res.json()
    assert analysis["possible_condition"] == "Respiratory Infection"
    assert analysis["risk_level"] == "HIGH"
    assert analysis["confidence"] == 87.0
    assert analysis["is_demo_inference"] is True
    assert analysis["veterinary_review_required"] is True
    assert len(analysis["recommended_immediate_actions"]) > 0
    assert "disclaimer" in analysis

    # Test Foot and Mouth Disease pattern
    payload_fmd = {
        "species": "Cattle",
        "temperature": "105.1 °F",
        "symptoms": ["Excessive salivation", "Vesicles on tongue and oral mucosa"],
        "observations": "Lameness and coronary band inflammation."
    }
    res_fmd = client.post("/api/detection/analyze", json=payload_fmd)
    assert res_fmd.status_code == 200
    analysis_fmd = res_fmd.json()
    assert "Foot and Mouth Disease" in analysis_fmd["possible_condition"]
    assert analysis_fmd["risk_level"] == "CRITICAL"

def test_veterinary_workflow_and_license_guard(client):
    """Test veterinary case retrieval, review notes, and medicine prescription guard."""
    # 1. Get cases
    cases_res = client.get("/api/veterinary/cases")
    assert cases_res.status_code == 200
    cases = cases_res.json()
    assert len(cases) >= 1
    case = cases[0]
    case_id = case["case_id"]

    # 2. Review case
    review_payload = {
        "vet_name": "Dr. Rajesh Patel",
        "vet_license_no": "VET-REG-88402-GJ",
        "final_diagnosis": "Confirmed Foot and Mouth Disease (Vesicular Lesions)",
        "review_notes": "Clinical quarantine enforced. Supportive antipyretic administered.",
        "case_status": "Under Clinical Treatment",
        "follow_up_date": "2026-10-10 (10:00 AM)"
    }
    review_res = client.put(f"/api/veterinary/cases/{case_id}/review", json=review_payload)
    assert review_res.status_code == 200, review_res.text
    reviewed = review_res.json()
    assert reviewed["attending_vet"] == "Dr. Rajesh Patel"
    assert reviewed["case_status"] == "Under Clinical Treatment"

    # 3. Add treatment with valid veterinary license
    treatment_payload = {
        "medicine_name": "Meloxicam Bolus 100mg",
        "dosage": "1 bolus PO once daily",
        "duration": "3 days",
        "instructions": "Administer with feed",
        "prescribing_vet_license": "VET-REG-88402-GJ",
        "attending_vet_name": "Dr. Rajesh Patel"
    }
    trt_res = client.post(f"/api/veterinary/cases/{case_id}/treatment", json=treatment_payload)
    assert trt_res.status_code == 201, trt_res.text
    updated_case = trt_res.json()
    assert any(t["medicine_name"] == "Meloxicam Bolus 100mg" for t in updated_case["treatments"])

    # 4. Attempt treatment without valid license (must be rejected)
    invalid_trt_payload = {
        "medicine_name": "Broad-spectrum Antibiotic",
        "dosage": "20 mL",
        "duration": "5 days",
        "instructions": "Self-administer",
        "prescribing_vet_license": "",  # Empty license
        "attending_vet_name": "Anonymous"
    }
    invalid_res = client.post(f"/api/veterinary/cases/{case_id}/treatment", json=invalid_trt_payload)
    assert invalid_res.status_code == 400
    assert "license" in invalid_res.text.lower()

def test_alerts_workflow(client):
    """Test biosecurity alert listing, creation, and acknowledgment."""
    # 1. List alerts
    alerts_res = client.get("/api/alerts")
    assert alerts_res.status_code == 200
    alerts_data = alerts_res.json()
    assert alerts_data["total"] >= 1
    assert "items" in alerts_data

    # 2. Create alert
    create_payload = {
        "title": "Suspected Anthrax Warning in Sector 14",
        "description": "Sudden unexplained livestock mortality reported in grazing pasture.",
        "alert_type": "critical",
        "severity": "Critical",
        "location": "North Meadow - Sector 14",
        "affected_tag": "TAG-9901",
        "action_required": "Do not open carcass. Contact District Epidemiologist immediately.",
        "dispatch_status": "Emergency Team Alerted"
    }
    created_res = client.post("/api/alerts", json=create_payload)
    assert created_res.status_code == 201, created_res.text
    created_alert = created_res.json()
    alert_id = created_alert["alert_id"]
    assert created_alert["alert_type"] == "critical"

    # 3. Acknowledge alert
    ack_res = client.put(
        f"/api/alerts/{alert_id}/acknowledge",
        json={"acknowledged_by": "Dr. Arvind Verma", "notes": "Quarantine team dispatched"}
    )
    assert ack_res.status_code == 200
    ack_data = ack_res.json()
    assert ack_data["status"] == "Acknowledged"
    assert ack_data["acknowledged_by"] == "Dr. Arvind Verma"
