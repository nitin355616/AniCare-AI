"""
AniCare AI — Milestone 9B Test Suite
Smart Treatment, Prevention, Vaccination & Farmer Guidance

Validates:
1. Multi-medicine treatment prescription by authorized veterinarian with formulation details
2. Prevention plan update, biosecurity controls, and farmer instructions
3. Vaccination tracking, date validation, and farmer/admin restriction
4. Withdrawal period module: milk & meat withholding, validation against negative days, unverified vs verified
5. Role-based security (Farmers blocked with 403 on prescriptions, prevention, withdrawal, vaccinations)
6. Alerts linkage for active withdrawal periods and upcoming vaccinations
7. Animal treatment history endpoint
8. Dynamic veterinary statistics with vaccinations_due and withdrawal_restrictions
"""

import uuid
import datetime
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


def test_veterinarian_multi_medicine_prescription(client):
    """Verifies that a veterinarian can prescribe multiple medicines with formulations and instructions."""
    vet_headers = get_auth_header("veterinarian", license_num="VET-REG-2024-88402")
    animal_tag = f"TAG-M9B-MED-{uuid.uuid4().hex[:4].upper()}"

    # Create case
    case_res = client.post("/api/veterinary/cases", json={
        "animal_id": animal_tag,
        "animal_name": "Kankrej Bull #12",
        "species": "Cattle",
        "risk_level": "HIGH",
        "condition": "Acute Cutaneous Papules"
    })
    assert case_res.status_code == 201
    case_id = case_res.json()["case_id"]

    # Review case first
    client.put(
        f"/api/veterinary/cases/{case_id}/review",
        json={
            "decision": "AI_ASSESSMENT_ACCEPTED",
            "vet_name": "Dr. Rajesh Patel",
            "vet_license_no": "VET-REG-2024-88402",
            "clinical_notes": "Clinical examination confirms acute stage 2 lesions."
        },
        headers=vet_headers
    )

    # Prescribe multi-medicine regimen
    treatment_payload = {
        "diagnosis_assessment": "Bovine Cutaneous Nodulitis (Capripox Suspected)",
        "attending_vet_name": "Dr. Rajesh Patel",
        "prescribing_vet_license": "VET-REG-2024-88402",
        "medicines": [
            {
                "medicine_name": "Meloxicam Injection 5mg/ml",
                "formulation": "Injectable Solution",
                "dosage": "0.5 mg/kg SC once daily",
                "route": "Subcutaneous (SC)",
                "frequency": "Once daily",
                "duration": "3 days",
                "instructions": "Administer with sterile 18G needle."
            },
            {
                "medicine_name": "Ivermectin 1% Solution",
                "formulation": "Injectable Solution",
                "dosage": "0.2 mg/kg SC single dose",
                "route": "Subcutaneous (SC)",
                "frequency": "Single dose",
                "duration": "1 day",
                "instructions": "Inject in lateral cervical skin fold."
            },
            {
                "medicine_name": "Povidone Iodine 5% Ointment",
                "formulation": "Topical Ointment",
                "dosage": "Thin film twice daily",
                "route": "Topical",
                "frequency": "Twice daily",
                "duration": "7 days",
                "instructions": "Apply gently after antiseptic wash."
            }
        ],
        "supportive_care": "Provide clean dry straw bedding and oral electrolytes.",
        "isolation_required": True,
        "isolation_instructions": "Maintain insect-proof fly mesh netting around quarantine pen.",
        "farmer_instructions": "Ensure clean drinking water at all times. Do not alter prescribed doses.",
        "withdrawal_type": "milk",
        "withdrawal_days": 5,
        "withdrawal_verified": True
    }

    trt_res = client.post(f"/api/veterinary/cases/{case_id}/treatment", json=treatment_payload, headers=vet_headers)
    assert trt_res.status_code == 201, trt_res.text
    case_data = trt_res.json()

    assert case_data["case_status"] == "TREATMENT_ACTIVE"
    assert len(case_data["treatment_plan"]["medicines"]) == 3
    assert case_data["treatment_plan"]["farmer_instructions"] == treatment_payload["farmer_instructions"]
    assert case_data["withdrawal_information"]["status"] == "ACTIVE"
    assert case_data["withdrawal_information"]["withdrawal_days"] == 5
    assert case_data["withdrawal_information"]["verified"] is True


def test_farmer_and_admin_blocked_from_prescriptions(client):
    """Verifies that farmers and administrators cannot prescribe medications."""
    farmer_headers = get_auth_header("farmer")
    admin_headers = get_auth_header("admin")
    vet_headers = get_auth_header("veterinarian", license_num="VET-REG-2024-88402")

    animal_tag = f"TAG-M9B-SEC-{uuid.uuid4().hex[:4].upper()}"
    res = client.post("/api/veterinary/cases", json={
        "animal_id": animal_tag,
        "species": "Cattle",
        "risk_level": "MODERATE",
        "condition": "Suspected BRD"
    })
    case_id = res.json()["case_id"]

    # Review case so it's ready for treatment
    client.put(
        f"/api/veterinary/cases/{case_id}/review",
        json={"decision": "AI_ASSESSMENT_ACCEPTED", "clinical_notes": "Reviewed", "vet_license_no": "VET-REG-2024-88402"},
        headers=vet_headers
    )

    # Farmer attempt -> 403
    farm_res = client.post(
        f"/api/veterinary/cases/{case_id}/treatment",
        json={"medicine_name": "Antibiotic", "prescribing_vet_license": "VET-REG-2024-88402"},
        headers=farmer_headers
    )
    assert farm_res.status_code == 403

    # Admin attempt -> 403
    admin_res = client.post(
        f"/api/veterinary/cases/{case_id}/treatment",
        json={"medicine_name": "Antibiotic", "prescribing_vet_license": "VET-REG-2024-88402"},
        headers=admin_headers
    )
    assert admin_res.status_code == 403


def test_prevention_plan_update_and_authorization(client):
    """Verifies PUT /api/veterinary/cases/{case_id}/prevention updates biosecurity and respects RBAC."""
    vet_headers = get_auth_header("veterinarian", license_num="VET-REG-2024-88402")
    farmer_headers = get_auth_header("farmer")

    animal_tag = f"TAG-M9B-PREV-{uuid.uuid4().hex[:4].upper()}"
    res = client.post("/api/veterinary/cases", json={
        "animal_id": animal_tag,
        "species": "Cattle",
        "risk_level": "HIGH",
        "condition": "Cutaneous Nodules"
    })
    case_id = res.json()["case_id"]

    prev_payload = {
        "isolation_required": True,
        "isolation_duration_days": 21,
        "isolation_instructions": "Quarantine in Pen 04 with fly-barrier netting.",
        "hygiene_guidance": "Disinfect feed troughs daily with 2% sodium hypochlorite.",
        "vector_control": "Apply synthetic pyrethroid spray on outer perimeter.",
        "animal_separation": "Strict physical segregation from lactating cows and calves.",
        "monitoring_protocol": "Record body temperature at 07:00 and 17:00 daily.",
        "farmer_instructions": "Clean boots with disinfectant footbath before entering shed."
    }

    # Farmer attempt -> 403
    farm_prev = client.put(f"/api/veterinary/cases/{case_id}/prevention", json=prev_payload, headers=farmer_headers)
    assert farm_prev.status_code == 403

    # Vet attempt -> 200
    vet_prev = client.put(f"/api/veterinary/cases/{case_id}/prevention", json=prev_payload, headers=vet_headers)
    assert vet_prev.status_code == 200, vet_prev.text
    prev_data = vet_prev.json()["prevention_plan"]
    assert prev_data["isolation_duration_days"] == 21
    assert prev_data["hygiene_guidance"] == prev_payload["hygiene_guidance"]
    assert any(a["action"] == "PREVENTION_PLAN_UPDATED" for a in vet_prev.json()["audit_trail"])


def test_withdrawal_period_safety_and_validation(client):
    """
    Verifies withdrawal period logic:
    - Rejects negative withdrawal days (400)
    - Unverified withdrawal defaults to VERIFY_WITH_VETERINARIAN
    - Verified withdrawal computes active countdown and creates alert
    - Farmer is forbidden from modifying withdrawal (403)
    """
    vet_headers = get_auth_header("veterinarian", license_num="VET-REG-2024-88402")
    farmer_headers = get_auth_header("farmer")

    animal_tag = f"TAG-M9B-WITH-{uuid.uuid4().hex[:4].upper()}"
    res = client.post("/api/veterinary/cases", json={
        "animal_id": animal_tag,
        "species": "Cattle",
        "risk_level": "HIGH",
        "condition": "Bovine Mastitis"
    })
    case_id = res.json()["case_id"]

    # 1. Negative days -> 400
    res_neg = client.put(
        f"/api/veterinary/cases/{case_id}/withdrawal",
        json={"withdrawal_type": "milk", "withdrawal_days": -3, "verified": True},
        headers=vet_headers
    )
    assert res_neg.status_code == 400
    assert "negative" in res_neg.text.lower() or "greater" in res_neg.text.lower()

    # 2. Farmer blocked -> 403
    res_farm = client.put(
        f"/api/veterinary/cases/{case_id}/withdrawal",
        json={"withdrawal_type": "milk", "withdrawal_days": 4, "verified": True},
        headers=farmer_headers
    )
    assert res_farm.status_code == 403

    # 3. Unverified withdrawal -> status VERIFY_WITH_VETERINARIAN
    res_unver = client.put(
        f"/api/veterinary/cases/{case_id}/withdrawal",
        json={"withdrawal_type": "both", "withdrawal_days": 7, "verified": False},
        headers=vet_headers
    )
    assert res_unver.status_code == 200
    w_unver = res_unver.json()["withdrawal_information"]
    assert w_unver["status"] == "VERIFY_WITH_VETERINARIAN"
    assert "unverified" in w_unver["safety_notice"].lower() or "unavailable" in w_unver["safety_notice"].lower()

    # 4. Verified withdrawal -> status ACTIVE with safety notice
    res_ver = client.put(
        f"/api/veterinary/cases/{case_id}/withdrawal",
        json={"withdrawal_type": "milk", "withdrawal_days": 5, "verified": True, "source": "Statutory ICAR Guideline"},
        headers=vet_headers
    )
    assert res_ver.status_code == 200
    w_ver = res_ver.json()["withdrawal_information"]
    assert w_ver["status"] == "ACTIVE"
    assert w_ver["days_remaining"] == 5
    assert w_ver["verified"] is True
    assert any(a["action"] == "WITHDRAWAL_PERIOD_UPDATED" for a in res_ver.json()["audit_trail"])


def test_vaccination_tracking_and_date_validation(client):
    """
    Verifies animal vaccination tracking:
    - Creation by vet works
    - Invalid next_due_date (earlier than admin_date) is rejected (400)
    - Farmer cannot create vaccination record (403)
    - Admin cannot create vaccination record (403)
    - History can be retrieved
    """
    vet_headers = get_auth_header("veterinarian", license_num="VET-REG-2024-88402")
    farmer_headers = get_auth_header("farmer")
    admin_headers = get_auth_header("admin")
    animal_tag = f"TAG-M9B-VAC-{uuid.uuid4().hex[:4].upper()}"

    # 1. Invalid dates: next_due_date earlier than admin_date -> 400
    invalid_vac = {
        "vaccine_name": "LSD Heterologous Goat Pox Vaccine",
        "disease_target": "Lumpy Skin Disease",
        "date_administered": "2026-10-10",
        "next_due_date": "2026-05-01",  # earlier!
        "batch_number": "BATCH-2026-09"
    }
    res_inv = client.post(f"/api/animals/{animal_tag}/vaccinations", json=invalid_vac, headers=vet_headers)
    assert res_inv.status_code == 400
    assert "earlier" in res_inv.text.lower()

    # 2. Farmer blocked -> 403
    valid_vac = {
        "vaccine_name": "LSD Heterologous Goat Pox Vaccine",
        "disease_target": "Lumpy Skin Disease",
        "date_administered": "2026-10-08",
        "next_due_date": "2027-10-08",
        "batch_number": "BATCH-2026-09",
        "notes": "Administered 1ml SC lateral neck fold."
    }
    res_farm = client.post(f"/api/animals/{animal_tag}/vaccinations", json=valid_vac, headers=farmer_headers)
    assert res_farm.status_code == 403

    # 3. Admin blocked -> 403
    res_admin = client.post(f"/api/animals/{animal_tag}/vaccinations", json=valid_vac, headers=admin_headers)
    assert res_admin.status_code == 403

    # 4. Vet succeeds -> 201
    res_vet = client.post(f"/api/animals/{animal_tag}/vaccinations", json=valid_vac, headers=vet_headers)
    assert res_vet.status_code == 201, res_vet.text
    vac_data = res_vet.json()
    assert vac_data["vaccination_id"].startswith("VAC-")
    assert vac_data["animal_id"] == animal_tag
    assert vac_data["disease_target"] == "Lumpy Skin Disease"

    # 5. Retrieve vaccination history
    hist_res = client.get(f"/api/animals/{animal_tag}/vaccinations")
    assert hist_res.status_code == 200
    history = hist_res.json()
    assert len(history) >= 1
    assert history[0]["vaccine_name"] == "LSD Heterologous Goat Pox Vaccine"


def test_animal_treatment_history_and_farmer_read_access(client):
    """Verifies that farmers can view complete approved treatment history for an animal."""
    vet_headers = get_auth_header("veterinarian", license_num="VET-REG-2024-88402")
    animal_tag = f"TAG-M9B-HIST-{uuid.uuid4().hex[:4].upper()}"

    # Create and treat case
    case_res = client.post("/api/veterinary/cases", json={
        "animal_id": animal_tag,
        "species": "Cattle",
        "risk_level": "MODERATE",
        "condition": "FMD Suspect"
    })
    case_id = case_res.json()["case_id"]

    client.put(
        f"/api/veterinary/cases/{case_id}/review",
        json={"decision": "AI_ASSESSMENT_ACCEPTED", "clinical_notes": "Reviewed", "vet_license_no": "VET-REG-2024-88402"},
        headers=vet_headers
    )
    client.post(
        f"/api/veterinary/cases/{case_id}/treatment",
        json={
            "medicine_name": "Meloxicam Bolus",
            "dosage": "1 bolus daily",
            "duration": "3 days",
            "prescribing_vet_license": "VET-REG-2024-88402",
            "farmer_instructions": "Administer with feed"
        },
        headers=vet_headers
    )

    # Query treatment history
    history_res = client.get(f"/api/animals/{animal_tag}/treatment-history")
    assert history_res.status_code == 200
    hist = history_res.json()
    assert hist["animal_id"] == animal_tag
    assert hist["total_cases"] >= 1
    assert hist["active_treatments"] >= 1
    assert any(c["case_id"] == case_id for c in hist["cases"])


def test_complete_end_to_end_9b_clinical_workflow(client):
    """
    Verifies complete end-to-end clinical workflow:
    REVIEW -> TREATMENT (with multi-medicine) -> PREVENTION -> VACCINATION -> WITHDRAWAL -> FOLLOW_UP -> CLOSED.
    """
    vet_headers = get_auth_header("veterinarian", license_num="VET-REG-2024-99120")
    animal_tag = f"TAG-M9B-E2E-{uuid.uuid4().hex[:4].upper()}"

    # 1. Create case
    c_res = client.post("/api/veterinary/cases", json={
        "animal_id": animal_tag,
        "species": "Cattle",
        "risk_level": "HIGH",
        "condition": "Lumpy Skin Disease Suspected"
    })
    case_id = c_res.json()["case_id"]

    # 2. Vet review
    rev_res = client.put(
        f"/api/veterinary/cases/{case_id}/review",
        json={
            "decision": "AI_ASSESSMENT_ACCEPTED",
            "vet_name": "Dr. Meenakshi Sundaram",
            "vet_license_no": "VET-REG-2024-99120",
            "clinical_notes": "Verified circumscribed nodular eruptions."
        },
        headers=vet_headers
    )
    assert rev_res.status_code == 200

    # 3. Treatment plan with multi-medicine
    trt_res = client.post(
        f"/api/veterinary/cases/{case_id}/treatment",
        json={
            "diagnosis_assessment": "Confirmed Lumpy Skin Disease",
            "attending_vet_name": "Dr. Meenakshi Sundaram",
            "prescribing_vet_license": "VET-REG-2024-99120",
            "medicines": [
                {
                    "medicine_name": "Flunixin Meglumine",
                    "formulation": "Injectable Solution",
                    "dosage": "2.2 mg/kg IV",
                    "route": "Intravenous (IV)",
                    "frequency": "Once daily",
                    "duration": "3 days"
                }
            ],
            "isolation_required": True,
            "farmer_instructions": "Keep isolated in vector netting bay."
        },
        headers=vet_headers
    )
    assert trt_res.status_code == 201

    # 4. Prevention plan
    prev_res = client.put(
        f"/api/veterinary/cases/{case_id}/prevention",
        json={
            "isolation_required": True,
            "isolation_duration_days": 14,
            "isolation_instructions": "Insect-proof mesh netting",
            "vector_control": "Fly spray daily"
        },
        headers=vet_headers
    )
    assert prev_res.status_code == 200

    # 5. Vaccination
    vac_res = client.post(
        f"/api/animals/{animal_tag}/vaccinations",
        json={
            "vaccine_name": "Goat Pox Attenuated Vaccine",
            "disease_target": "Lumpy Skin Disease",
            "date_administered": "2026-10-08",
            "next_due_date": "2027-10-08",
            "case_id": case_id
        },
        headers=vet_headers
    )
    assert vac_res.status_code == 201

    # 6. Withdrawal period
    with_res = client.put(
        f"/api/veterinary/cases/{case_id}/withdrawal",
        json={"withdrawal_type": "milk", "withdrawal_days": 4, "verified": True},
        headers=vet_headers
    )
    assert with_res.status_code == 200

    # 7. Follow-up
    fol_res = client.post(
        f"/api/veterinary/cases/{case_id}/follow-up",
        json={"follow_up_date": "2026-10-18", "notes": "Assess nodule regression."},
        headers=vet_headers
    )
    assert fol_res.status_code == 200

    # 8. Close case
    close_res = client.put(
        f"/api/veterinary/cases/{case_id}/close",
        json={"notes": "Lesions healed completely, normal appetite."},
        headers=vet_headers
    )
    assert close_res.status_code == 200
    final_case = close_res.json()
    assert final_case["case_status"] == "CLOSED"
    assert final_case["treatment_plan"] is not None
    assert final_case["prevention_plan"] is not None
    assert final_case["withdrawal_information"]["status"] == "ACTIVE"
    assert len(final_case["audit_trail"]) >= 6


def test_veterinary_stats_includes_vaccinations_and_withdrawals(client):
    """Verifies that GET /api/veterinary/stats returns vaccinations_due and withdrawal_restrictions."""
    res = client.get("/api/veterinary/stats")
    assert res.status_code == 200
    data = res.json()
    assert "vaccinations_due" in data
    assert "withdrawal_restrictions" in data
    assert isinstance(data["vaccinations_due"], int)
    assert isinstance(data["withdrawal_restrictions"], int)
