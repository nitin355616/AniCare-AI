"""
AniCare AI — Milestone 9D Test Suite
Farmer Experience, Multilingual & Low-Literacy UX

Validates:
1. Low-literacy dashboard structure and aggregated herd metrics
2. Simplified non-technical status categorization (HEALTHY, ATTENTION, URGENT)
3. Dual-language (Hindi/English) explanations and actionable next steps
4. Strict farmer privacy guard: Farmer B blocked (HTTP 403) from accessing Farmer A's animal
5. Direct doctor visit request submission and alert dispatching
6. Doctor-approved treatment transparency and milk withdrawal food safety notices
7. Localized, non-alarmist public health outbreak warnings
8. Veterinarian and admin authorized clinical access bypass
"""

import uuid
import pytest
from app.utils.security import create_access_token

def get_farmer_auth_header(name: str = "Kishorbhai Patel", email: str = "kishor.patel@anicare.org", role: str = "farmer") -> dict:
    uid = f"usr_{uuid.uuid4().hex[:6]}"
    payload = {
        "sub": uid,
        "role": role,
        "email": email,
        "name": name
    }
    token = create_access_token(payload)
    return {"Authorization": f"Bearer {token}"}

def test_farmer_dashboard_structure(client):
    """Verifies that the farmer dashboard returns simplified counts, outbreak warning, and animal summaries."""
    res = client.get("/api/farmer/dashboard")
    assert res.status_code == 200
    data = res.json()

    assert "farmer_name" in data
    assert "farmer_location" in data
    assert "total_animals" in data
    assert "healthy_count" in data
    assert "attention_count" in data
    assert "urgent_count" in data
    assert "outbreak_warning" in data
    assert "animals" in data
    assert isinstance(data["animals"], list)
    assert data["total_animals"] == len(data["animals"])

def test_farmer_simplified_status_bilingual_labels(client):
    """Verifies that every animal has simplified status and complete Hindi/English explanations."""
    res = client.get("/api/farmer/dashboard")
    assert res.status_code == 200
    animals = res.json()["animals"]

    for a in animals:
        assert a["simplified_status"] in ["HEALTHY", "ATTENTION", "URGENT"]
        assert isinstance(a["status_label_en"], str) and len(a["status_label_en"]) > 0
        assert isinstance(a["status_label_hi"], str) and len(a["status_label_hi"]) > 0
        assert isinstance(a["explanation_en"], str) and len(a["explanation_en"]) > 0
        assert isinstance(a["explanation_hi"], str) and len(a["explanation_hi"]) > 0
        assert isinstance(a["action_needed"], bool)

def test_farmer_animal_detail_action_steps(client):
    """Verifies that animal detail provides action-first steps with bilingual guidance."""
    dash_res = client.get("/api/farmer/dashboard")
    assert dash_res.status_code == 200
    animals = dash_res.json()["animals"]
    assert len(animals) > 0

    animal_id = animals[0]["animal_id"]
    det_res = client.get(f"/api/farmer/animals/{animal_id}")
    assert det_res.status_code == 200
    detail = det_res.json()

    assert detail["animal_id"] == animal_id
    assert "action_steps" in detail
    assert len(detail["action_steps"]) >= 2

    for step in detail["action_steps"]:
        assert "step_number" in step
        assert "title_en" in step and len(step["title_en"]) > 0
        assert "title_hi" in step and len(step["title_hi"]) > 0
        assert "description_en" in step and len(step["description_en"]) > 0
        assert "description_hi" in step and len(step["description_hi"]) > 0
        assert step["urgency"] in ["routine", "important", "critical"]

    assert "vet_helpline" in detail
    assert detail["vet_helpline"] is not None

def test_farmer_privacy_guard_enforcement(client):
    """Strictly verifies that Farmer B receives HTTP 403 when trying to access or request visits for Farmer A's animal."""
    # Farmer A owns Ganga at Amul farm
    farmer_a_headers = get_farmer_auth_header(name="Kishorbhai Patel", email="kishor@anandfarm.org")
    # Farmer B owns a different farm in Rajasthan/Punjab
    farmer_b_headers = get_farmer_auth_header(name="Ramesh Kumar", email="ramesh.kumar@farms.in")

    target_animal_id = "AN-GJ-2024-0104"

    # Farmer A can access
    res_a = client.get(f"/api/farmer/animals/{target_animal_id}", headers=farmer_a_headers)
    assert res_a.status_code in [200, 404]

    # Farmer B must be blocked with 403 Forbidden
    res_b = client.get(f"/api/farmer/animals/{target_animal_id}", headers=farmer_b_headers)
    assert res_b.status_code == 403
    err_b = res_b.json().get("error") or res_b.json().get("detail") or ""
    assert "forbidden" in err_b.lower()

    # Farmer B cannot request a review for Farmer A's animal
    req_b = client.post(
        f"/api/farmer/animals/{target_animal_id}/request-review",
        json={"symptoms": ["Lethargy"], "notes": "Unauthorized probe"},
        headers=farmer_b_headers
    )
    assert req_b.status_code == 403
    err_req_b = req_b.json().get("error") or req_b.json().get("detail") or ""
    assert "forbidden" in err_req_b.lower()

def test_farmer_doctor_visit_request_success(client):
    """Verifies that an authorized farmer can request an immediate doctor visit."""
    farmer_headers = get_farmer_auth_header(name="Kishorbhai Patel")
    target_animal_id = "AN-GJ-2024-0104"

    res = client.post(
        f"/api/farmer/animals/{target_animal_id}/request-review",
        json={
            "symptoms": ["High Fever", "Skin lumps"],
            "notes": "Cow has high fever and is not chewing cud since morning.",
            "preferred_time": "Morning"
        },
        headers=farmer_headers
    )

    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert "case_id" in data
    assert "message_en" in data and len(data["message_en"]) > 0
    assert "message_hi" in data and len(data["message_hi"]) > 0

def test_treatment_plan_and_withdrawal_notice(client):
    """Verifies that medical treatment plans explicitly display doctor approval and food safety notices."""
    target_animal_id = "AN-GJ-2024-0104"
    res = client.get(f"/api/farmer/animals/{target_animal_id}")
    assert res.status_code == 200
    data = res.json()

    assert "withdrawal_notice" in data
    wd = data["withdrawal_notice"]
    assert wd is not None
    assert "is_active" in wd
    assert "warning_message_en" in wd
    assert "warning_message_hi" in wd

    # Check treatment plan doctor approval note
    tp = data.get("treatment_plan")
    if tp and tp.get("is_active"):
        assert "doctor_approved_notice_en" in tp
        assert "doctor_approved_notice_hi" in tp
        assert "certified veterinary doctor" in tp["doctor_approved_notice_en"].lower()

def test_farmer_outbreak_warning_endpoint(client):
    """Verifies the localized public health advisory endpoint for farmers."""
    res = client.get("/api/farmer/outbreak-warning")
    assert res.status_code == 200
    data = res.json()

    assert "has_warning" in data
    assert "severity" in data
    assert "title_en" in data and len(data["title_en"]) > 0
    assert "title_hi" in data and len(data["title_hi"]) > 0
    assert "message_en" in data and len(data["message_en"]) > 0
    assert "message_hi" in data and len(data["message_hi"]) > 0
    assert "action_en" in data and len(data["action_en"]) > 0
    assert "action_hi" in data and len(data["action_hi"]) > 0

def test_vet_and_admin_bypass_privacy_guard(client):
    """Verifies that veterinarians and admins can inspect any animal across herds for clinical supervision."""
    vet_headers = get_farmer_auth_header(name="Dr. Rajesh Patel", role="veterinarian")
    admin_headers = get_farmer_auth_header(name="Chief Admin", role="admin")
    target_animal_id = "AN-GJ-2024-0104"

    res_vet = client.get(f"/api/farmer/animals/{target_animal_id}", headers=vet_headers)
    assert res_vet.status_code == 200

    res_admin = client.get(f"/api/farmer/animals/{target_animal_id}", headers=admin_headers)
    assert res_admin.status_code == 200
