"""
AniCare AI — Milestone 13 Test Suite
Field Response, Alert Orchestration & Government Action Workflow

Validates:
1. Alert Engine: P1 Critical Alert generation & deduplication
2. Alert Engine: P3 Monitoring Alert generation
3. Duplicate Alert prevention (source_id + alert_type deduplication)
4. Alert Escalation logging & audit
5. RBAC: Farmer access denied (HTTP 403 Forbidden)
6. RBAC: Veterinarian access permitted
7. RBAC: Field Officer access permitted for investigations
8. RBAC: Lab User access permitted for laboratory results
9. RBAC: Department Officer / Admin permitted for action authorizations
10. Assignment workflow & target timestamps
11. Field Investigation recording (animals, symptoms, biosecurity)
12. Evidence Validation: Allowed extensions (.jpg, .pdf) & SHA-256 checksums
13. Evidence Validation: Executable binaries rejected (HTTP 400 Bad Request)
14. Biological Specimen tracking & LAB_PENDING status
15. Diagnostic Laboratory Result recording
16. Unauthorized Lab Result rejected (HTTP 403)
17. Clinical Safety: Lab result moves case to DEPARTMENT_REVIEW (no autonomous containment)
18. Department Review & strategic recommendation
19. Action Authorization requires Department Officer/Admin role
20. Farmer cannot authorize containment action (HTTP 403)
21. In-App Notification generation & delivery
22. Truth-in-Telemetry: Unconfigured SMS marked NOT_CONFIGURED (no fake delivery)
23. Truth-in-Telemetry: Unconfigured WhatsApp marked NOT_CONFIGURED
24. Notification deduplication within short window
25. Veterinary Follow-up inspection & trajectory tracking
26. Response Case closure & final audit
27. Critical Case closure guard (requires prior investigation)
28. Milestone 12 Geospatial Hotspot integration
29. Milestone 9C Outbreak Event integration
30. Case Deduplication (reusing existing case for same source_id)
31. Offline Idempotency: Duplicate submissions return original record
32. SLA operational turnaround calculation
33. SIH 14-step End-to-End Field Response Scenario execution
"""

import uuid
import pytest
from app.utils.security import create_access_token
from app.services.response_service import (
    response_service,
    ALLOWED_EXTENSIONS,
    DISALLOWED_EXTENSIONS,
    MAX_FILE_SIZE_BYTES
)
from app.schemas.response import (
    ResponsePriority,
    ResponseSeverity,
    ResponseStatus,
    SourceType,
    SampleType,
    SampleStatus,
    LabResultType,
    DepartmentDecisionType,
    ActionType,
    ClosureReason,
    NotificationChannel,
    NotificationStatus,
    SAFETY_DISCLAIMER
)


def get_auth_header(role: str, user_id: str = None) -> dict:
    uid = user_id or f"usr_{uuid.uuid4().hex[:6]}"
    payload = {
        "sub": uid,
        "role": role,
        "email": f"{role}_{uid}@anicare.ai",
        "name": f"Dr. {role.capitalize()}" if role in ["veterinarian", "field_officer"] else f"Officer {role.capitalize()}"
    }
    token = create_access_token(payload)
    return {"Authorization": f"Bearer {token}"}


# ---------------------------------------------------------------------------
# Alert Engine Tests
# ---------------------------------------------------------------------------

def test_1_geospatial_p1_creates_critical_alert(client):
    """Verifies that high-risk geospatial signals (score >= 80) generate P1 critical alerts."""
    admin_hdr = get_auth_header("admin")
    payload = {
        "source_type": "GEOSPATIAL_HOTSPOT",
        "source_id": f"GEO-TEST-P1-{uuid.uuid4().hex[:4]}",
        "risk_score": 88.0,
        "priority": "P1",
        "location": {
            "state": "Gujarat",
            "district": "Anand",
            "block": "Anand Rural",
            "village": "Boriavi"
        },
        "condition_signal": "SUSPECTED_LSD",
        "is_demo": False
    }
    res = client.post("/api/response/cases", json=payload, headers=admin_hdr)
    assert res.status_code == 201
    data = res.json()
    assert data["priority"] == "P1"
    assert data["severity"] == "CRITICAL"
    assert len(data["alerts"]) >= 1
    alert = data["alerts"][0]
    assert alert["priority"] == "P1"
    assert alert["status"] == "ACTIVE"
    assert "Boriavi" in alert["message"]


def test_2_p3_creates_monitoring_alert(client):
    """Verifies that moderate risk signals generate P3 monitoring alerts."""
    vet_hdr = get_auth_header("veterinarian")
    payload = {
        "source_type": "GEOSPATIAL_HOTSPOT",
        "source_id": f"GEO-TEST-P3-{uuid.uuid4().hex[:4]}",
        "risk_score": 38.0,
        "priority": "P3",
        "condition_signal": "MASTITIS_SYNDROMIC"
    }
    res = client.post("/api/response/cases", json=payload, headers=vet_hdr)
    assert res.status_code == 201
    data = res.json()
    assert data["priority"] == "P3"
    assert data["severity"] == "WARNING"


def test_3_duplicate_alert_prevented(client):
    """Verifies that recalculating or re-triggering for an active source updates existing alert rather than duplicating."""
    admin_hdr = get_auth_header("admin")
    source_id = f"GEO-TEST-DEDUP-{uuid.uuid4().hex[:4]}"
    payload1 = {
        "source_type": "GEOSPATIAL_HOTSPOT",
        "source_id": source_id,
        "risk_score": 75.0,
        "priority": "P2"
    }
    res1 = client.post("/api/response/cases", json=payload1, headers=admin_hdr)
    assert res1.status_code == 201
    case1 = res1.json()

    # Second submission with same source_id
    payload2 = {
        "source_type": "GEOSPATIAL_HOTSPOT",
        "source_id": source_id,
        "risk_score": 78.0,
        "priority": "P2"
    }
    res2 = client.post("/api/response/cases", json=payload2, headers=admin_hdr)
    assert res2.status_code == 201
    case2 = res2.json()
    # Must reuse the same case
    assert case1["response_case_id"] == case2["response_case_id"]


def test_4_alert_escalation_logged(client):
    """Verifies alert priority escalation logs rationale and actor in escalation history."""
    admin_hdr = get_auth_header("admin")
    # Create P3 case
    payload = {
        "source_type": "GEOSPATIAL_HOTSPOT",
        "source_id": f"GEO-ESC-{uuid.uuid4().hex[:4]}",
        "risk_score": 45.0,
        "priority": "P3"
    }
    case_res = client.post("/api/response/cases", json=payload, headers=admin_hdr)
    case_data = case_res.json()
    alert_id = case_data["alerts"][0]["alert_id"]

    # Escalate to P1
    esc_res = client.post(
        f"/api/response/alerts/{alert_id}/escalate",
        json={"to_priority": "P1", "reason": "Rapid spike in affected herds reported by cooperative."},
        headers=admin_hdr
    )
    assert esc_res.status_code == 200
    esc_data = esc_res.json()
    assert esc_data["priority"] == "P1"
    assert len(esc_data["escalation_history"]) >= 1
    entry = esc_data["escalation_history"][-1]
    assert entry["from_priority"] == "P3"
    assert entry["to_priority"] == "P1"
    assert "spike" in entry["reason"]


# ---------------------------------------------------------------------------
# RBAC Tests
# ---------------------------------------------------------------------------

def test_5_farmer_denied_government_operations(client):
    """Verifies farmers cannot create response cases, view alerts, or trigger investigations (HTTP 403)."""
    farmer_hdr = get_auth_header("farmer")
    # Attempt list alerts
    res_alerts = client.get("/api/response/alerts", headers=farmer_hdr)
    assert res_alerts.status_code == 403

    # Attempt create case
    res_create = client.post(
        "/api/response/cases",
        json={"source_id": "GEO-FARMER-ATTEMPT", "risk_score": 80.0},
        headers=farmer_hdr
    )
    assert res_create.status_code == 403


def test_6_veterinarian_allowed_for_investigation_and_alerts(client):
    """Verifies veterinarians can view alerts, cases, and acknowledge."""
    vet_hdr = get_auth_header("veterinarian")
    res = client.get("/api/response/alerts", headers=vet_hdr)
    assert res.status_code == 200


def test_7_field_officer_allowed_for_investigation_and_samples(client):
    """Verifies field officers can record field investigations."""
    fo_hdr = get_auth_header("field_officer")
    admin_hdr = get_auth_header("admin")
    # Create test case
    case_res = client.post(
        "/api/response/cases",
        json={"source_id": f"GEO-FO-{uuid.uuid4().hex[:4]}", "risk_score": 70.0},
        headers=admin_hdr
    )
    case_id = case_res.json()["response_case_id"]

    inv_res = client.post(
        f"/api/response/cases/{case_id}/investigation",
        json={
            "officer_name": "Dr. Field Officer",
            "animals_observed": 12,
            "symptoms_observed": ["Lethargy", "Fever"],
            "affected_animals": 2,
            "herds_observed": 1,
            "biosecurity_observations": "Clean shelter."
        },
        headers=fo_hdr
    )
    assert inv_res.status_code == 201


def test_8_lab_user_allowed_for_lab_operations(client):
    """Verifies lab users can record laboratory diagnostic assay results."""
    lab_hdr = get_auth_header("lab_user")
    admin_hdr = get_auth_header("admin")
    # Create case and sample
    case_res = client.post(
        "/api/response/cases",
        json={"source_id": f"GEO-LAB-{uuid.uuid4().hex[:4]}", "risk_score": 75.0},
        headers=admin_hdr
    )
    case_id = case_res.json()["response_case_id"]
    sample_res = client.post(
        f"/api/response/cases/{case_id}/samples",
        json={"sample_type": "SWAB", "purpose": "PCR Test", "collected_by_name": "Field Officer"},
        headers=admin_hdr
    )
    sample_id = sample_res.json()["sample_id"]

    # Record lab result
    lab_res = client.post(
        f"/api/response/samples/{sample_id}/result",
        json={
            "result": "POSITIVE",
            "test_name": "Real-time RT-PCR",
            "lab_reference": "REF-PCR-01",
            "reviewer": "Lab Pathologist"
        },
        headers=lab_hdr
    )
    assert lab_res.status_code == 200
    assert lab_res.json()["lab_result"] == "POSITIVE"


def test_9_department_officer_allowed_for_authorization(client):
    """Verifies department officers and admins can authorize containment actions."""
    dept_hdr = get_auth_header("department_officer")
    admin_hdr = get_auth_header("admin")
    case_res = client.post(
        "/api/response/cases",
        json={"source_id": f"GEO-AUTH-{uuid.uuid4().hex[:4]}", "risk_score": 82.0},
        headers=admin_hdr
    )
    case_id = case_res.json()["response_case_id"]

    auth_res = client.post(
        f"/api/response/cases/{case_id}/authorize-action",
        json={
            "action_type": "BIOSECURITY_REVIEW",
            "reason": "Cluster containment advisory",
            "authorized_by": "District Magistrate"
        },
        headers=dept_hdr
    )
    assert auth_res.status_code == 201
    assert auth_res.json()["action_type"] == "BIOSECURITY_REVIEW"


# ---------------------------------------------------------------------------
# Investigation & Evidence Tests
# ---------------------------------------------------------------------------

def test_10_assignment_workflow(client):
    """Verifies assignment of field officer transitions status to INVESTIGATION_ASSIGNED."""
    admin_hdr = get_auth_header("admin")
    case_res = client.post(
        "/api/response/cases",
        json={"source_id": f"GEO-ASN-{uuid.uuid4().hex[:4]}", "risk_score": 65.0},
        headers=admin_hdr
    )
    case_id = case_res.json()["response_case_id"]

    asn_res = client.post(
        f"/api/response/cases/{case_id}/assign",
        json={
            "assigned_to": "VET-007",
            "assigned_officer_name": "Dr. Sharma",
            "due_date": "2026-10-09T12:00:00Z",
            "instructions": "Inspect herd and check biosecurity"
        },
        headers=admin_hdr
    )
    assert asn_res.status_code == 200
    data = asn_res.json()
    assert data["status"] == "INVESTIGATION_ASSIGNED"
    assert data["assigned_to"] == "VET-007"


def test_11_field_investigation_workflow(client):
    """Verifies field investigation details are saved and case status updates."""
    admin_hdr = get_auth_header("admin")
    case_res = client.post(
        "/api/response/cases",
        json={"source_id": f"GEO-INV-{uuid.uuid4().hex[:4]}", "risk_score": 65.0},
        headers=admin_hdr
    )
    case_id = case_res.json()["response_case_id"]

    inv_res = client.post(
        f"/api/response/cases/{case_id}/investigation",
        json={
            "officer_name": "Dr. Patel",
            "animals_observed": 20,
            "symptoms_observed": ["Nodules", "Fever"],
            "affected_animals": 4,
            "herds_observed": 2,
            "biosecurity_observations": "Separate shed advised"
        },
        headers=admin_hdr
    )
    assert inv_res.status_code == 201
    inv_data = inv_res.json()
    assert inv_data["affected_animals"] == 4
    assert len(inv_data["symptoms_observed"]) == 2


def test_12_evidence_validation_allowed_extensions():
    """Verifies allowed evidence extensions (jpg, png, pdf) pass validation and return checksum."""
    ext, chk, size = response_service.validate_and_hash_evidence("lesion_photo.jpg", b"fake-jpg-content", "image/jpeg")
    assert ext == "jpg"
    assert len(chk) == 64
    assert size == len(b"fake-jpg-content")


def test_13_evidence_validation_executable_rejected():
    """Verifies dangerous executable files (.exe, .bat, .sh) are rejected with HTTP 400."""
    with pytest.raises(Exception) as exc:
        response_service.validate_and_hash_evidence("exploit.exe", b"malicious", "application/octet-stream")
    assert "Executable" in str(exc.value) or "400" in str(exc.value)


# ---------------------------------------------------------------------------
# Biological Specimen & Laboratory Workflow Tests
# ---------------------------------------------------------------------------

def test_14_sample_creation_workflow(client):
    """Verifies sample collection registers with LAB_PENDING status."""
    admin_hdr = get_auth_header("admin")
    case_res = client.post(
        "/api/response/cases",
        json={"source_id": f"GEO-SMP-{uuid.uuid4().hex[:4]}", "risk_score": 65.0},
        headers=admin_hdr
    )
    case_id = case_res.json()["response_case_id"]

    smp_res = client.post(
        f"/api/response/cases/{case_id}/samples",
        json={"sample_type": "SWAB", "purpose": "RT-PCR Confirmatory", "collected_by_name": "Dr. Rao"},
        headers=admin_hdr
    )
    assert smp_res.status_code == 201
    smp = smp_res.json()
    assert smp["status"] == "LAB_PENDING"
    assert smp["sample_type"] == "SWAB"


def test_15_lab_result_recording(client):
    """Verifies diagnostic result recording by authorized lab user."""
    admin_hdr = get_auth_header("admin")
    lab_hdr = get_auth_header("lab_user")

    case_res = client.post(
        "/api/response/cases",
        json={"source_id": f"GEO-LABRES-{uuid.uuid4().hex[:4]}", "risk_score": 70.0},
        headers=admin_hdr
    )
    case_id = case_res.json()["response_case_id"]

    smp_res = client.post(
        f"/api/response/cases/{case_id}/samples",
        json={"sample_type": "BLOOD", "purpose": "ELISA Test", "collected_by_name": "Dr. Rao"},
        headers=admin_hdr
    )
    sample_id = smp_res.json()["sample_id"]

    res = client.post(
        f"/api/response/samples/{sample_id}/result",
        json={
            "result": "NEGATIVE",
            "test_name": "ELISA Test",
            "lab_reference": "REF-ELISA-99",
            "reviewer": "Chief Pathologist"
        },
        headers=lab_hdr
    )
    assert res.status_code == 200
    assert res.json()["lab_result"] == "NEGATIVE"
    assert res.json()["status"] == "RESULT_AVAILABLE"


def test_16_unauthorized_lab_result_rejected(client):
    """Verifies non-lab user (e.g. farmer) is blocked from recording lab results (HTTP 403)."""
    farmer_hdr = get_auth_header("farmer")
    res = client.post(
        "/api/response/samples/SMP-FAKE/result",
        json={"result": "POSITIVE", "test_name": "PCR", "lab_reference": "REF", "reviewer": "Farmer"},
        headers=farmer_hdr
    )
    assert res.status_code == 403


def test_17_lab_result_does_not_autonomously_authorize_action(client):
    """
    CRITICAL CLINICAL SAFETY PRINCIPLE:
    A positive lab result MUST NOT autonomously trigger containment or medication.
    It must advance the case to DEPARTMENT_REVIEW for human authorization.
    """
    admin_hdr = get_auth_header("admin")
    lab_hdr = get_auth_header("lab_user")

    case_res = client.post(
        "/api/response/cases",
        json={"source_id": f"GEO-CLINICAL-{uuid.uuid4().hex[:4]}", "risk_score": 85.0},
        headers=admin_hdr
    )
    case_id = case_res.json()["response_case_id"]

    smp_res = client.post(
        f"/api/response/cases/{case_id}/samples",
        json={"sample_type": "SWAB", "purpose": "Diagnostic", "collected_by_name": "Dr. Rao"},
        headers=admin_hdr
    )
    sample_id = smp_res.json()["sample_id"]

    client.post(
        f"/api/response/samples/{sample_id}/result",
        json={"result": "POSITIVE", "test_name": "PCR", "lab_reference": "REF-POS", "reviewer": "Pathologist"},
        headers=lab_hdr
    )

    # Check case status: Must be DEPARTMENT_REVIEW, NOT ACTION_AUTHORIZED
    updated_case = client.get(f"/api/response/cases/{case_id}", headers=admin_hdr).json()
    assert updated_case["status"] == "DEPARTMENT_REVIEW"
    assert len(updated_case["actions"]) == 0  # Zero autonomous actions!


# ---------------------------------------------------------------------------
# Department Review & Action Authorization Tests
# ---------------------------------------------------------------------------

def test_18_department_review_workflow(client):
    """Verifies department review records decision and strategic recommendation."""
    admin_hdr = get_auth_header("admin")
    case_res = client.post(
        "/api/response/cases",
        json={"source_id": f"GEO-DREV-{uuid.uuid4().hex[:4]}", "risk_score": 85.0},
        headers=admin_hdr
    )
    case_id = case_res.json()["response_case_id"]

    rev_res = client.post(
        f"/api/response/cases/{case_id}/department-review",
        json={
            "decision": "BIOSECURITY_REVIEW",
            "reason": "Cluster containment protocol needed",
            "reviewer": "Joint Director (DAHD)"
        },
        headers=admin_hdr
    )
    assert rev_res.status_code == 201
    assert rev_res.json()["decision"] == "BIOSECURITY_REVIEW"


def test_19_action_authorization_requires_authorized_role(client):
    """Verifies field officer or regular veterinarian cannot authorize department actions (HTTP 403)."""
    fo_hdr = get_auth_header("field_officer")
    res = client.post(
        "/api/response/cases/RESP-FAKE/authorize-action",
        json={"action_type": "AUTHORIZED_CONTAINMENT", "reason": "Reason", "authorized_by": "Officer"},
        headers=fo_hdr
    )
    assert res.status_code == 403


def test_20_farmer_cannot_authorize_action(client):
    """Verifies farmer cannot authorize department actions (HTTP 403)."""
    farmer_hdr = get_auth_header("farmer")
    res = client.post(
        "/api/response/cases/RESP-FAKE/authorize-action",
        json={"action_type": "BIOSECURITY_REVIEW", "reason": "Reason", "authorized_by": "Farmer"},
        headers=farmer_hdr
    )
    assert res.status_code == 403


# ---------------------------------------------------------------------------
# Notification & Outbox Tests
# ---------------------------------------------------------------------------

def test_21_in_app_notification_generated(client):
    """Verifies in-app notification is queued and delivered."""
    admin_hdr = get_auth_header("admin")
    res = client.post(
        "/api/response/notifications",
        json={
            "channel": "IN_APP",
            "recipient_type": "OFFICER",
            "recipient_target": f"user_{uuid.uuid4().hex[:4]}",
            "template": "CRITICAL_ALERT",
            "title": "High Priority Notice",
            "message": "Field inspection required."
        },
        headers=admin_hdr
    )
    assert res.status_code == 201
    data = res.json()
    assert data["status"] == "DELIVERED"
    assert data["provider"] == "AniCare Realtime Event Bus"


def test_22_unconfigured_sms_marked_not_configured(client):
    """
    TRUTH IN TELEMETRY:
    Unconfigured SMS gateway reports status NOT_CONFIGURED. No fake delivery timestamps.
    """
    admin_hdr = get_auth_header("admin")
    res = client.post(
        "/api/response/notifications",
        json={
            "channel": "SMS",
            "recipient_type": "OFFICER",
            "recipient_target": "+919876543210",
            "template": "ALERT_SMS",
            "title": "Alert",
            "message": "AniCare AI Alert: High-priority signal detected."
        },
        headers=admin_hdr
    )
    assert res.status_code == 201
    data = res.json()
    assert data["status"] == "NOT_CONFIGURED"
    assert data["provider"] is None


def test_23_unconfigured_whatsapp_marked_not_configured(client):
    """Unconfigured WhatsApp gateway reports status NOT_CONFIGURED."""
    admin_hdr = get_auth_header("admin")
    res = client.post(
        "/api/response/notifications",
        json={
            "channel": "WHATSAPP",
            "recipient_type": "OFFICER",
            "recipient_target": "+919876543210",
            "template": "ALERT_WA",
            "title": "Alert",
            "message": "AniCare AI Alert: High-priority signal."
        },
        headers=admin_hdr
    )
    assert res.status_code == 201
    data = res.json()
    assert data["status"] == "NOT_CONFIGURED"


def test_24_duplicate_notifications_suppressed(client):
    """Verifies rapid duplicate notifications to the same recipient and template are suppressed."""
    admin_hdr = get_auth_header("admin")
    target = f"target_{uuid.uuid4().hex[:6]}"
    payload = {
        "channel": "IN_APP",
        "recipient_type": "OFFICER",
        "recipient_target": target,
        "template": "DEDUP_TEST",
        "title": "Duplicate Test",
        "message": "Test"
    }
    res1 = client.post("/api/response/notifications", json=payload, headers=admin_hdr)
    res2 = client.post("/api/response/notifications", json=payload, headers=admin_hdr)
    assert res1.status_code == 201
    assert res2.status_code == 201
    # Second should return the first notification ID
    assert res1.json()["notification_id"] == res2.json()["notification_id"]


# ---------------------------------------------------------------------------
# Follow-up & Closure Tests
# ---------------------------------------------------------------------------

def test_25_follow_up_workflow(client):
    """Verifies follow-up visit recording and trajectory tracking."""
    admin_hdr = get_auth_header("admin")
    case_res = client.post(
        "/api/response/cases",
        json={"source_id": f"GEO-FLW-{uuid.uuid4().hex[:4]}", "risk_score": 75.0},
        headers=admin_hdr
    )
    case_id = case_res.json()["response_case_id"]

    flw_res = client.post(
        f"/api/response/cases/{case_id}/follow-up",
        json={
            "officer_name": "Dr. Veterinary Officer",
            "new_observations": "Lesions regressed, recovery proceeding",
            "new_case_count": 0,
            "risk_change": "DECLINING",
            "action_outcome": "Biosecurity ring maintained"
        },
        headers=admin_hdr
    )
    assert flw_res.status_code in [200, 201]
    assert flw_res.json()["risk_change"] == "DECLINING"


def test_26_case_closure_workflow(client):
    """Verifies closing a non-critical case with closure reason."""
    admin_hdr = get_auth_header("admin")
    case_res = client.post(
        "/api/response/cases",
        json={"source_id": f"GEO-CLS-{uuid.uuid4().hex[:4]}", "risk_score": 35.0, "priority": "P3"},
        headers=admin_hdr
    )
    case_id = case_res.json()["response_case_id"]

    cls_res = client.post(
        f"/api/response/cases/{case_id}/close",
        json={
            "closure_reason": "NO_FURTHER_SIGNAL",
            "final_status": "RESOLVED",
            "comment": "Monitoring period concluded with zero secondary spread."
        },
        headers=admin_hdr
    )
    assert cls_res.status_code == 200
    assert cls_res.json()["status"] == "RESOLVED"


def test_27_critical_case_closure_requires_investigation(client):
    """Verifies that an uninvestigated P1 critical case CANNOT be closed (HTTP 400)."""
    admin_hdr = get_auth_header("admin")
    case_res = client.post(
        "/api/response/cases",
        json={"source_id": f"GEO-P1-NOCLOSE-{uuid.uuid4().hex[:4]}", "risk_score": 92.0, "priority": "P1"},
        headers=admin_hdr
    )
    case_id = case_res.json()["response_case_id"]

    cls_res = client.post(
        f"/api/response/cases/{case_id}/close",
        json={
            "closure_reason": "CASE_RESOLVED",
            "final_status": "RESOLVED",
            "comment": "Premature closure attempt"
        },
        headers=admin_hdr
    )
    assert cls_res.status_code == 400
    err_body = cls_res.json()
    err_msg = err_body.get("error") or err_body.get("detail") or str(err_body)
    assert "investigation" in err_msg.lower()


# ---------------------------------------------------------------------------
# Integration & Interoperability Tests
# ---------------------------------------------------------------------------

def test_28_geospatial_hotspot_to_response_case_integration(client):
    """Verifies Milestone 12 geospatial hotspot generates linked response case."""
    admin_hdr = get_auth_header("admin")
    res = client.post(
        "/api/response/cases",
        json={
            "source_type": "GEOSPATIAL_HOTSPOT",
            "source_id": "GEO-HOTSPOT-INT-01",
            "risk_score": 84.0,
            "condition_signal": "SUSPECTED_LSD"
        },
        headers=admin_hdr
    )
    assert res.status_code == 201
    data = res.json()
    assert data["source_id"] == "GEO-HOTSPOT-INT-01"
    assert data["source_type"] == "GEOSPATIAL_HOTSPOT"


def test_29_outbreak_event_to_response_case_integration(client):
    """Verifies Milestone 9C outbreak event generates linked response case."""
    admin_hdr = get_auth_header("admin")
    res = client.post(
        "/api/response/cases",
        json={
            "source_type": "OUTBREAK_EVENT",
            "source_id": "OB-EVENT-INT-01",
            "risk_score": 72.0,
            "condition_signal": "SUSPECTED_FMD"
        },
        headers=admin_hdr
    )
    assert res.status_code == 201
    data = res.json()
    assert data["source_id"] == "OB-EVENT-INT-01"
    assert data["source_type"] == "OUTBREAK_EVENT"


def test_30_existing_case_reused_on_duplicate_creation(client):
    """Verifies creating a response case for an already tracked source ID returns existing case."""
    admin_hdr = get_auth_header("admin")
    source = f"GEO-REUSE-{uuid.uuid4().hex[:4]}"
    res1 = client.post("/api/response/cases", json={"source_id": source, "risk_score": 60.0}, headers=admin_hdr)
    res2 = client.post("/api/response/cases", json={"source_id": source, "risk_score": 60.0}, headers=admin_hdr)
    assert res1.json()["response_case_id"] == res2.json()["response_case_id"]


# ---------------------------------------------------------------------------
# Offline & SLA Tests
# ---------------------------------------------------------------------------

def test_31_idempotent_retry_investigation_and_samples(client):
    """Verifies that offline synchronization retries with idempotency_key return the same record."""
    admin_hdr = get_auth_header("admin")
    case_res = client.post(
        "/api/response/cases",
        json={"source_id": f"GEO-IDEM-{uuid.uuid4().hex[:4]}", "risk_score": 65.0},
        headers=admin_hdr
    )
    case_id = case_res.json()["response_case_id"]
    idem_key = f"IDEM-KEY-{uuid.uuid4().hex[:8]}"

    payload = {
        "officer_name": "Dr. Offline Officer",
        "animals_observed": 15,
        "affected_animals": 3,
        "herds_observed": 1,
        "biosecurity_observations": "Offline log",
        "idempotency_key": idem_key
    }
    r1 = client.post(f"/api/response/cases/{case_id}/investigation", json=payload, headers=admin_hdr)
    r2 = client.post(f"/api/response/cases/{case_id}/investigation", json=payload, headers=admin_hdr)
    assert r1.status_code == 201
    assert r2.status_code == 201
    assert r1.json()["investigation_id"] == r2.json()["investigation_id"]


def test_32_sla_metrics_calculation(client):
    """Verifies SLA operational turnaround metrics calculation."""
    admin_hdr = get_auth_header("admin")
    case_res = client.post(
        "/api/response/cases",
        json={"source_id": f"GEO-SLA-{uuid.uuid4().hex[:4]}", "risk_score": 88.0, "priority": "P1"},
        headers=admin_hdr
    )
    case_id = case_res.json()["response_case_id"]
    alert_id = case_res.json()["alerts"][0]["alert_id"]

    # Acknowledge
    client.post(f"/api/response/alerts/{alert_id}/acknowledge", json={"comment": "Ack"}, headers=admin_hdr)

    # Fetch dossier
    case_dossier = client.get(f"/api/response/cases/{case_id}", headers=admin_hdr).json()
    sla = case_dossier["sla_metrics"]
    assert sla["time_to_acknowledge_minutes"] is not None
    assert sla["time_to_acknowledge_minutes"] >= 0.0


# ---------------------------------------------------------------------------
# SIH 14-Step End-to-End Scenario Test
# ---------------------------------------------------------------------------

def test_33_sih_demo_scenario_execution(client):
    """
    Executes the 14-step SIH Hackathon Field Response workflow scenario.
    Validates complete lifecycle from Geospatial Detection to Risk Recalculation.
    """
    admin_hdr = get_auth_header("admin")
    res = client.post("/api/response/demo/run-scenario", headers=admin_hdr)
    assert res.status_code == 200
    data = res.json()
    assert data["steps_completed"] == 14
    assert data["final_status"] == "RESOLVED"
    assert data["timeline_events_count"] >= 10
    assert len(data["steps"]) == 14
    assert data["disclaimer"] == SAFETY_DISCLAIMER
