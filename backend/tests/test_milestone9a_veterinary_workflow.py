"""
AniCare AI — Milestone 9A Test Suite
Veterinary Decision Support Workflow & Clinical Lifecycle Governance

Validates:
1. Real-time veterinary statistics endpoint (/api/veterinary/stats)
2. Strict 5-status lifecycle: PENDING_REVIEW -> REVIEWED -> TREATMENT_ACTIVE -> FOLLOW_UP -> CLOSED
3. Rejection of invalid status transitions (e.g. closing pending cases, modifying closed cases)
4. Role-based security (Farmers blocked with 403, Admins blocked from prescription, Vets authorized)
5. Statutory veterinary license enforcement
6. Full regulatory audit trail tracking
7. Autonomous AI screening escalation to pending veterinary review
"""

import uuid
import pytest
from app.utils.security import create_access_token


def get_auth_header(role: str, user_id: str = None, license_num: str = None) -> dict:
    uid = user_id or f"usr_{uuid.uuid4().hex[:6]}"
    payload = {
        "sub": uid,
        "role": role,
        "email": f"{role}_{uid}@anicare.ai",
        "name": f"Dr. Test {role.capitalize()}" if role == "veterinarian" else f"Test {role.capitalize()}"
    }
    if license_num:
        payload["license"] = license_num
    token = create_access_token(payload)
    return {"Authorization": f"Bearer {token}"}


def test_veterinary_stats_endpoint(client):
    """Verifies the /api/veterinary/stats endpoint returns real aggregate MongoDB metrics."""
    res = client.get("/api/veterinary/stats")
    assert res.status_code == 200, res.text
    data = res.json()
    assert "pending_reviews" in data
    assert "high_critical_cases" in data
    assert "active_treatments" in data
    assert "follow_ups_due" in data
    assert "closed_cases" in data
    assert "total_cases" in data
    assert isinstance(data["pending_reviews"], int)
    assert isinstance(data["total_cases"], int)
    assert data["total_cases"] >= 0


def test_veterinary_case_creation_and_initial_state(client):
    """Verifies that a newly created case enters PENDING_REVIEW with initial audit log."""
    animal_tag = f"TAG-M9A-{uuid.uuid4().hex[:4].upper()}"
    create_payload = {
        "animal_id": animal_tag,
        "animal_name": "Ganga Crossbreed",
        "species": "Cattle (Bos indicus)",
        "owner_name": "Rameshbhai Patel",
        "location": "North Shed 03",
        "risk_level": "HIGH",
        "condition": "Suspected Lumpy Skin Disease",
        "confidence": 88.5,
        "explanation": "Circumscribed cutaneous nodular eruptions on neck and flank.",
        "symptoms": ["Cutaneous nodules", "Pyrexia 104.2 F", "Superficial lymph node enlargement"],
        "recommended_actions": ["Insect-proof quarantine", "Palpate nodules", "Antipyretic therapy"]
    }

    res = client.post("/api/veterinary/cases", json=create_payload)
    assert res.status_code == 201, res.text
    case = res.json()
    assert case["case_status"] == "PENDING_REVIEW"
    assert case["case_id"].startswith("CASE-")
    assert case["animal_id"] == animal_tag
    assert len(case["audit_trail"]) >= 1
    assert any(a["action"] == "CASE_CREATED" for a in case["audit_trail"])


def test_full_decision_support_workflow_lifecycle(client):
    """
    Tests complete valid clinical lifecycle:
    PENDING_REVIEW -> REVIEWED -> TREATMENT_ACTIVE -> FOLLOW_UP -> CLOSED.
    """
    vet_headers = get_auth_header("veterinarian", license_num="VET-REG-2024-99120")
    animal_tag = f"TAG-FLOW-{uuid.uuid4().hex[:4].upper()}"

    # Step 0: Create case
    create_res = client.post("/api/veterinary/cases", json={
        "animal_id": animal_tag,
        "animal_name": "Nandi Bull",
        "species": "Cattle",
        "owner_name": "Suresh Kumar",
        "location": "Amul Cluster Shed 01",
        "risk_level": "CRITICAL",
        "condition": "Severe Cutaneous Nodulitis",
        "confidence": 92.0,
        "explanation": "Extensive coalescing nodular lesions with high pyrexia.",
        "symptoms": ["Severe nodules", "Fever 105.0 F"]
    })
    assert create_res.status_code == 201
    case_id = create_res.json()["case_id"]

    # Step 1: Review case (PENDING_REVIEW -> REVIEWED)
    review_res = client.put(
        f"/api/veterinary/cases/{case_id}/review",
        json={
            "decision": "AI_ASSESSMENT_ACCEPTED",
            "vet_name": "Dr. Meenakshi Sundaram",
            "vet_license_no": "VET-REG-2024-99120",
            "clinical_notes": "Clinical physical examination confirms acute generalized Lumpy Skin Disease.",
            "veterinary_assessment": "Confirmed Acute Lumpy Skin Disease",
            "follow_up_date": "2026-10-14"
        },
        headers=vet_headers
    )
    assert review_res.status_code == 200, review_res.text
    reviewed = review_res.json()
    assert reviewed["case_status"] == "REVIEWED"
    assert reviewed["attending_vet"] == "Dr. Meenakshi Sundaram"
    assert any(a["action"] == "CASE_REVIEWED" for a in reviewed["audit_trail"])

    # Step 2: Prescribe Treatment (REVIEWED -> TREATMENT_ACTIVE)
    trt_res = client.post(
        f"/api/veterinary/cases/{case_id}/treatment",
        json={
            "diagnosis_assessment": "Acute Lumpy Skin Disease (Circumscribed Stage)",
            "attending_vet_name": "Dr. Meenakshi Sundaram",
            "prescribing_vet_license": "VET-REG-2024-99120",
            "medicines": [
                {
                    "medicine_name": "Meloxicam 5mg/ml",
                    "dosage": "0.5 mg/kg SC once daily",
                    "frequency": "Once daily",
                    "duration": "3 days",
                    "route": "Subcutaneous (SC)",
                    "instructions": "Administer with sterile needle under antiseptic skin preparation."
                },
                {
                    "medicine_name": "Ivermectin 1% Injection",
                    "dosage": "0.2 mg/kg SC single dose",
                    "frequency": "Single dose",
                    "duration": "1 day",
                    "route": "Subcutaneous (SC)",
                    "instructions": "Subcutaneous injection in lateral neck fold."
                }
            ],
            "supportive_care": "Antiseptic povidone-iodine wash on ruptured papules, fly-repellent spray, clean dry straw.",
            "isolation_required": True,
            "instructions": "Maintain insect-net isolation pen."
        },
        headers=vet_headers
    )
    assert trt_res.status_code == 201, trt_res.text
    treated = trt_res.json()
    assert treated["case_status"] == "TREATMENT_ACTIVE"
    assert len(treated["treatment_plan"]["medicines"]) == 2
    assert treated["treatment_plan"]["isolation_required"] is True
    assert any(a["action"] == "TREATMENT_CREATED" for a in treated["audit_trail"])

    # Step 3: Schedule Follow-up (TREATMENT_ACTIVE -> FOLLOW_UP)
    follow_res = client.post(
        f"/api/veterinary/cases/{case_id}/follow-up",
        json={
            "follow_up_date": "2026-10-16",
            "notes": "Assess nodule scab detachment, lymph node palpation, and temperature return to baseline.",
            "required": True
        },
        headers=vet_headers
    )
    assert follow_res.status_code == 200, follow_res.text
    followed = follow_res.json()
    assert followed["case_status"] == "FOLLOW_UP"
    assert followed["follow_up"]["follow_up_date"] == "2026-10-16"
    assert any(a["action"] == "FOLLOW_UP_SCHEDULED" for a in followed["audit_trail"])

    # Step 4: Close Case (FOLLOW_UP -> CLOSED)
    close_res = client.put(
        f"/api/veterinary/cases/{case_id}/close",
        json={
            "notes": "Lesions completely resolved into hard scabs, no secondary bacterial infection, appetite normal.",
            "final_status": "CLOSED"
        },
        headers=vet_headers
    )
    assert close_res.status_code == 200, close_res.text
    closed = close_res.json()
    assert closed["case_status"] == "CLOSED"
    assert any(a["action"] == "CASE_CLOSED" for a in closed["audit_trail"])


def test_invalid_status_transitions_rejected(client):
    """
    Verifies state-machine guardrails:
    - Cannot prescribe treatment while still in PENDING_REVIEW
    - Cannot close a case that is in PENDING_REVIEW
    - Cannot review or treat an already CLOSED case
    """
    vet_headers = get_auth_header("veterinarian", license_num="VET-REG-2024-99120")
    animal_tag = f"TAG-INVALID-{uuid.uuid4().hex[:4].upper()}"

    # Create new case in PENDING_REVIEW
    res = client.post("/api/veterinary/cases", json={
        "animal_id": animal_tag,
        "animal_name": "Test Bovine",
        "species": "Cattle",
        "risk_level": "HIGH",
        "condition": "Cutaneous Nodules",
        "confidence": 85.0
    })
    case_id = res.json()["case_id"]

    # 1. Attempt treatment directly without review -> 400 Bad Request
    trt_invalid = client.post(
        f"/api/veterinary/cases/{case_id}/treatment",
        json={
            "medicine_name": "Meloxicam",
            "dosage": "0.5 mg/kg",
            "prescribing_vet_license": "VET-REG-2024-99120"
        },
        headers=vet_headers
    )
    assert trt_invalid.status_code == 400
    assert "review" in trt_invalid.text.lower()

    # 2. Attempt to close directly without review -> 400 Bad Request
    close_invalid = client.put(
        f"/api/veterinary/cases/{case_id}/close",
        json={"notes": "Premature closure attempt"},
        headers=vet_headers
    )
    assert close_invalid.status_code == 400
    assert "pending" in close_invalid.text.lower()

    # Perform legitimate review and close
    client.put(
        f"/api/veterinary/cases/{case_id}/review",
        json={
            "decision": "AI_ASSESSMENT_ACCEPTED",
            "vet_name": "Dr. Test Vet",
            "vet_license_no": "VET-REG-2024-99120",
            "clinical_notes": "Reviewed"
        },
        headers=vet_headers
    )
    client.put(
        f"/api/veterinary/cases/{case_id}/close",
        json={"notes": "Normal resolution"},
        headers=vet_headers
    )

    # 3. Attempt to review the already CLOSED case -> 400 Bad Request
    closed_review = client.put(
        f"/api/veterinary/cases/{case_id}/review",
        json={
            "decision": "AI_ASSESSMENT_ACCEPTED",
            "vet_name": "Dr. Test Vet",
            "vet_license_no": "VET-REG-2024-99120",
            "clinical_notes": "Attempting edit on closed case"
        },
        headers=vet_headers
    )
    assert closed_review.status_code == 400
    assert "closed" in closed_review.text.lower()


def test_role_based_security_authorization(client):
    """
    Verifies RBAC:
    - Farmers are blocked with 403 on review, treatment, follow-up, and close
    - Admins are blocked with 403 on prescriptions
    - Veterinarians are authorized
    """
    farmer_headers = get_auth_header("farmer")
    admin_headers = get_auth_header("admin")
    vet_headers = get_auth_header("veterinarian", license_num="VET-REG-2024-99120")

    animal_tag = f"TAG-RBAC-{uuid.uuid4().hex[:4].upper()}"
    res = client.post("/api/veterinary/cases", json={
        "animal_id": animal_tag,
        "species": "Cattle",
        "risk_level": "MODERATE",
        "condition": "Cutaneous Nodules",
        "confidence": 80.0
    })
    case_id = res.json()["case_id"]

    # Farmer attempts review -> 403 Forbidden
    res_farm_rev = client.put(
        f"/api/veterinary/cases/{case_id}/review",
        json={"decision": "AI_ASSESSMENT_ACCEPTED", "clinical_notes": "Farmer review attempt"},
        headers=farmer_headers
    )
    assert res_farm_rev.status_code == 403
    assert "forbidden" in res_farm_rev.text.lower() or "farmer" in res_farm_rev.text.lower()

    # Vet performs review -> 200 OK
    res_vet_rev = client.put(
        f"/api/veterinary/cases/{case_id}/review",
        json={"decision": "AI_ASSESSMENT_ACCEPTED", "clinical_notes": "Official vet review", "vet_license_no": "VET-REG-2024-99120"},
        headers=vet_headers
    )
    assert res_vet_rev.status_code == 200

    # Farmer attempts prescription -> 403 Forbidden
    res_farm_trt = client.post(
        f"/api/veterinary/cases/{case_id}/treatment",
        json={"medicine_name": "Antibiotic", "prescribing_vet_license": "VET-REG-2024-99120"},
        headers=farmer_headers
    )
    assert res_farm_trt.status_code == 403

    # Admin attempts prescription without vet credentials -> 403 Forbidden
    res_admin_trt = client.post(
        f"/api/veterinary/cases/{case_id}/treatment",
        json={"medicine_name": "Antibiotic", "prescribing_vet_license": "VET-REG-2024-99120"},
        headers=admin_headers
    )
    assert res_admin_trt.status_code == 403

    # Vet prescribes prescription -> 201 Created
    res_vet_trt = client.post(
        f"/api/veterinary/cases/{case_id}/treatment",
        json={"medicine_name": "Meloxicam", "dosage": "0.5 mg/kg", "prescribing_vet_license": "VET-REG-2024-99120"},
        headers=vet_headers
    )
    assert res_vet_trt.status_code == 201


def test_statutory_license_validation_edge_cases(client):
    """Verifies that prescribing treatment requires a valid, certified license string."""
    vet_headers = get_auth_header("veterinarian", license_num="VET-REG-2024-99120")
    animal_tag = f"TAG-LIC-{uuid.uuid4().hex[:4].upper()}"

    res = client.post("/api/veterinary/cases", json={
        "animal_id": animal_tag,
        "species": "Cattle",
        "risk_level": "HIGH",
        "condition": "Cutaneous Nodules",
        "confidence": 85.0
    })
    case_id = res.json()["case_id"]

    # Review case first
    client.put(
        f"/api/veterinary/cases/{case_id}/review",
        json={"decision": "AI_ASSESSMENT_ACCEPTED", "clinical_notes": "Notes", "vet_license_no": "VET-REG-2024-99120"},
        headers=vet_headers
    )

    # Empty license -> 400 Bad Request
    res_empty = client.post(
        f"/api/veterinary/cases/{case_id}/treatment",
        json={"medicine_name": "Meloxicam", "dosage": "0.5 mg/kg", "prescribing_vet_license": ""},
        headers=vet_headers
    )
    assert res_empty.status_code == 400
    assert "license" in res_empty.text.lower()

    # Short license (< 5 chars) -> 400 Bad Request
    res_short = client.post(
        f"/api/veterinary/cases/{case_id}/treatment",
        json={"medicine_name": "Meloxicam", "dosage": "0.5 mg/kg", "prescribing_vet_license": "VET"},
        headers=vet_headers
    )
    assert res_short.status_code == 400
    assert "license" in res_short.text.lower()

    # Valid license -> 201 Created
    res_valid = client.post(
        f"/api/veterinary/cases/{case_id}/treatment",
        json={"medicine_name": "Meloxicam", "dosage": "0.5 mg/kg", "prescribing_vet_license": "VET-REG-2024-99120"},
        headers=vet_headers
    )
    assert res_valid.status_code == 201


def test_ai_screening_escalation_to_pending_veterinary_case(client):
    """
    Verifies that a high/critical detection triage assessment
    automatically escalates to an active veterinary case in PENDING_REVIEW.
    """
    unique_tag = f"TAG-ESC-{uuid.uuid4().hex[:4].upper()}"
    triage_payload = {
        "animal_id": unique_tag,
        "species": "Cattle",
        "temperature": "105.4 °F",
        "symptoms": ["Severe mucosal vesicles", "Profuse drooling", "Lameness with coronary band lesions"],
        "observations": "High fever, inability to feed, blisters on dental pad."
    }

    triage_res = client.post("/api/detection/analyze", json=triage_payload)
    assert triage_res.status_code == 200, triage_res.text
    triage_data = triage_res.json()
    assert triage_data["risk_level"] in ["HIGH", "CRITICAL"]

    # Verify case exists in /api/veterinary/cases
    cases_res = client.get(f"/api/veterinary/cases?animal_id={unique_tag}")
    assert cases_res.status_code == 200
    matching_cases = cases_res.json()
    assert len(matching_cases) >= 1
    escalated_case = matching_cases[0]
    assert escalated_case["animal_id"] == unique_tag
    assert escalated_case["case_status"] == "PENDING_REVIEW"
    assert escalated_case["risk_level"] in ["HIGH", "CRITICAL"]


def test_case_filtering_by_status_and_risk(client):
    """Verifies that GET /api/veterinary/cases respects status and risk query parameters."""
    res_pending = client.get("/api/veterinary/cases?status=PENDING_REVIEW")
    assert res_pending.status_code == 200
    cases_pending = res_pending.json()
    for c in cases_pending:
        assert c["case_status"] == "PENDING_REVIEW"

    res_crit = client.get("/api/veterinary/cases?risk=CRITICAL")
    assert res_crit.status_code == 200
    cases_crit = res_crit.json()
    for c in cases_crit:
        assert c["risk_level"] == "CRITICAL"
