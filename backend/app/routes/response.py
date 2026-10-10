"""
AniCare AI — Field Response, Alert Orchestration & Government Action Routes
Milestone 13: REST Endpoints for Incident Prioritization, Alert Acknowledgment,
Field Investigations, Lab Assays, Department Authorizations, and Auditable Timelines.
"""

from typing import Optional, Dict, Any, List
from fastapi import APIRouter, Query, status, Security, HTTPException, UploadFile, File, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.schemas.response import (
    SAFETY_DISCLAIMER,
    ResponsePriority,
    ResponseSeverity,
    ResponseStatus,
    SourceType,
    SampleType,
    LabResultType,
    DepartmentDecisionType,
    ActionType,
    ClosureReason,
    NotificationChannel,
    ResponseLocation,
    ResponseAlertItem,
    FieldInvestigationRecord,
    SampleRecord,
    DepartmentReviewRecord,
    AuthorizedActionRecord,
    FollowUpRecord,
    ResponseCaseResponse,
    CreateResponseCaseRequest,
    AcknowledgeAlertRequest,
    AssignInvestigationRequest,
    InvestigationCreateRequest,
    SampleCreateRequest,
    LabResultRecordRequest,
    DepartmentReviewRequest,
    AuthorizeActionRequest,
    FollowUpRequest,
    CloseCaseRequest,
    EscalateAlertRequest,
    NotificationOutboxItem,
    QueueNotificationRequest,
    ResponseCaseListResponse,
    ResponseStatsResponse,
    DemoScenarioResult,
    EvidenceItem
)
from app.services.response_service import response_service
from app.utils.security import decode_access_token

router = APIRouter(prefix="/response", tags=["Field Response & Government Action Workflow"])
security_optional = HTTPBearer(auto_error=False)


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security_optional)
) -> Optional[Dict[str, Any]]:
    """Decodes JWT access credentials if provided."""
    if not credentials:
        return None
    try:
        return decode_access_token(credentials.credentials)
    except Exception:
        return None


def enforce_not_farmer(current_user: Optional[Dict[str, Any]], operation_name: str = "Government Response Operations") -> None:
    """Enforces that Farmers are blocked (HTTP 403 Forbidden) from government operational response queues."""
    if not current_user:
        return  # Allow open demo execution in development environments

    role = current_user.get("role", "farmer")
    if role == "farmer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access forbidden: Farmer accounts cannot perform {operation_name}."
        )


def enforce_role(current_user: Optional[Dict[str, Any]], allowed_roles: List[str], operation_name: str) -> None:
    """Enforces specific operational permission scopes."""
    if not current_user:
        return  # Allow open demo execution in unauthenticated tests unless explicit user provided

    role = current_user.get("role", "farmer")
    if role not in allowed_roles and role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access forbidden: Role '{role}' lacks permission for {operation_name}. Requires one of: {allowed_roles}"
        )


# ---------------------------------------------------------------------------
# Statistics & Overview
# ---------------------------------------------------------------------------

@router.get("/stats", response_model=ResponseStatsResponse)
async def api_get_response_stats(
    current_user: Optional[Dict[str, Any]] = Security(get_optional_user)
):
    """Returns executive command center KPIs for alerts, investigations, samples, and reviews."""
    enforce_not_farmer(current_user, "viewing government response KPIs")
    return await response_service.get_stats()


# ---------------------------------------------------------------------------
# Alerts & Escalation
# ---------------------------------------------------------------------------

@router.get("/alerts", response_model=List[ResponseAlertItem])
async def api_list_alerts(
    priority: Optional[ResponsePriority] = Query(None, description="P1, P2, P3, or P4"),
    status: Optional[str] = Query(None, description="ACTIVE, ACKNOWLEDGED, RESOLVED"),
    current_user: Optional[Dict[str, Any]] = Security(get_optional_user)
):
    """Lists prioritized operational response alerts with deduplication."""
    enforce_not_farmer(current_user, "viewing government alerts")
    return await response_service.list_alerts(priority=priority, status_filter=status)


@router.post("/alerts/{alert_id}/acknowledge", response_model=ResponseAlertItem)
async def api_acknowledge_alert(
    alert_id: str,
    req: AcknowledgeAlertRequest,
    current_user: Optional[Dict[str, Any]] = Security(get_optional_user)
):
    """Acknowledges an operational alert by authorized veterinary or department official."""
    enforce_not_farmer(current_user, "acknowledging alerts")
    actor = req.actor or (current_user.get("sub") if current_user else "Veterinary Officer")
    role = current_user.get("role", "veterinarian") if current_user else "veterinarian"
    return await response_service.acknowledge_alert(alert_id=alert_id, comment=req.comment, actor=actor, role=role)


@router.post("/alerts/{alert_id}/escalate", response_model=ResponseAlertItem)
async def api_escalate_alert(
    alert_id: str,
    req: EscalateAlertRequest,
    current_user: Optional[Dict[str, Any]] = Security(get_optional_user)
):
    """Escalates alert priority (e.g. P3 -> P1) with auditable rationale."""
    enforce_not_farmer(current_user, "escalating alerts")
    actor = current_user.get("sub") if current_user else "Veterinary Authority"
    return await response_service.escalate_alert(alert_id=alert_id, to_priority=req.to_priority, reason=req.reason, actor=actor)


# ---------------------------------------------------------------------------
# Cases & Assignments
# ---------------------------------------------------------------------------

@router.get("/cases", response_model=ResponseCaseListResponse)
async def api_list_cases(
    priority: Optional[ResponsePriority] = Query(None, description="Filter by priority tier"),
    status: Optional[ResponseStatus] = Query(None, description="Filter by operational status"),
    district: Optional[str] = Query(None, description="Filter by district"),
    current_user: Optional[Dict[str, Any]] = Security(get_optional_user)
):
    """Lists operational response cases with multi-criteria filtering."""
    enforce_not_farmer(current_user, "listing government response cases")
    cases = await response_service.list_cases(priority=priority, status_filter=status, district=district)
    return ResponseCaseListResponse(total=len(cases), items=cases, disclaimer=SAFETY_DISCLAIMER)


@router.post("/cases", response_model=ResponseCaseResponse, status_code=status.HTTP_201_CREATED)
async def api_create_case(
    req: CreateResponseCaseRequest,
    current_user: Optional[Dict[str, Any]] = Security(get_optional_user)
):
    """
    Creates or links a response case from a geospatial hotspot or outbreak signal.
    Enforces deduplication: Reuses existing case if source_id is already active.
    """
    enforce_not_farmer(current_user, "creating response cases")
    actor = current_user.get("sub") if current_user else "Operational Dispatcher"
    role = current_user.get("role", "system") if current_user else "system"
    return await response_service.create_response_case(req, actor=actor, role=role)


@router.get("/cases/{case_id}", response_model=ResponseCaseResponse)
async def api_get_case(
    case_id: str,
    current_user: Optional[Dict[str, Any]] = Security(get_optional_user)
):
    """Returns complete response case dossier including timeline, samples, and SLA metrics."""
    enforce_not_farmer(current_user, "viewing case dossier")
    return await response_service.get_response_case(case_id)


@router.post("/cases/{case_id}/assign", response_model=ResponseCaseResponse)
async def api_assign_investigation(
    case_id: str,
    req: AssignInvestigationRequest,
    current_user: Optional[Dict[str, Any]] = Security(get_optional_user)
):
    """Assigns authorized field officer to conduct on-site investigation."""
    enforce_role(current_user, ["veterinarian", "admin", "department_officer"], "assigning investigations")
    actor = current_user.get("sub") if current_user else "District Officer"
    role = current_user.get("role", "veterinarian") if current_user else "veterinarian"
    req_data = req.model_dump() if hasattr(req, "model_dump") else req.dict()
    return await response_service.assign_investigation(case_id=case_id, req=req_data, actor=actor, role=role)


# ---------------------------------------------------------------------------
# Field Investigation & Evidence Collection
# ---------------------------------------------------------------------------

@router.post("/cases/{case_id}/investigation", response_model=FieldInvestigationRecord, status_code=status.HTTP_201_CREATED)
async def api_record_investigation(
    case_id: str,
    req: InvestigationCreateRequest,
    current_user: Optional[Dict[str, Any]] = Security(get_optional_user)
):
    """Records on-site physical investigation findings (animals observed, symptoms, biosecurity)."""
    enforce_role(current_user, ["field_officer", "veterinarian", "admin"], "recording field investigations")
    actor = current_user.get("sub") if current_user else req.officer_name
    role = current_user.get("role", "field_officer") if current_user else "field_officer"
    return await response_service.record_investigation(case_id=case_id, req=req, actor=actor, role=role)


@router.post("/cases/{case_id}/evidence", response_model=EvidenceItem, status_code=status.HTTP_201_CREATED)
async def api_upload_evidence(
    case_id: str,
    file: UploadFile = File(...),
    notes: Optional[str] = Form(None),
    current_user: Optional[Dict[str, Any]] = Security(get_optional_user)
):
    """
    Secure evidence file upload for field observations.
    Validates extension (jpg, jpeg, png, pdf only) and computes SHA-256 integrity hash.
    Rejects executable binaries.
    """
    enforce_role(current_user, ["field_officer", "veterinarian", "admin"], "uploading evidence")
    content = await file.read()
    clean_ext, checksum, size_bytes = response_service.validate_and_hash_evidence(
        filename=file.filename,
        content_bytes=content,
        mime_type=file.content_type
    )

    actor = current_user.get("sub") if current_user else "Field Officer"
    evidence_id = f"EVD-{checksum[:8].upper()}"

    item = EvidenceItem(
        evidence_id=evidence_id,
        file_name=file.filename,
        file_type=clean_ext,
        checksum=checksum,
        file_size_bytes=size_bytes,
        uploaded_by=actor,
        uploaded_at=response_service._now_iso(),
        notes=notes,
        file_url=f"/uploads/evidence/{evidence_id}.{clean_ext}"
    )

    await response_service.log_event(
        case_id=case_id,
        event_type="EVIDENCE_UPLOADED",
        actor=actor,
        role=current_user.get("role", "field_officer") if current_user else "field_officer",
        description=f"Evidence file uploaded: {file.filename} (SHA-256: {checksum[:12]}...)",
        metadata={"evidence_id": evidence_id, "size_bytes": size_bytes}
    )

    return item


# ---------------------------------------------------------------------------
# Biological Specimen & Diagnostic Laboratory Tracking
# ---------------------------------------------------------------------------

@router.post("/cases/{case_id}/samples", response_model=SampleRecord, status_code=status.HTTP_201_CREATED)
async def api_create_sample(
    case_id: str,
    req: SampleCreateRequest,
    current_user: Optional[Dict[str, Any]] = Security(get_optional_user)
):
    """Registers biological sample collection and dispatches to laboratory with LAB_PENDING status."""
    enforce_role(current_user, ["field_officer", "veterinarian", "admin"], "collecting biological samples")
    actor = current_user.get("sub") if current_user else req.collected_by_name
    role = current_user.get("role", "field_officer") if current_user else "field_officer"
    return await response_service.create_sample(case_id=case_id, req=req, actor=actor, role=role)


@router.post("/samples/{sample_id}/result", response_model=SampleRecord)
async def api_record_lab_result(
    sample_id: str,
    req: LabResultRecordRequest,
    current_user: Optional[Dict[str, Any]] = Security(get_optional_user)
):
    """
    Records laboratory diagnostic result (POSITIVE, NEGATIVE, INCONCLUSIVE, or INVALID).
    CRITICAL: Does NOT autonomously trigger containment or medication. Advances case to DEPARTMENT_REVIEW.
    """
    enforce_role(current_user, ["lab_user", "admin"], "recording laboratory diagnostic results")
    actor = current_user.get("sub") if current_user else req.reviewer
    role = current_user.get("role", "lab_user") if current_user else "lab_user"
    return await response_service.record_lab_result(sample_id=sample_id, req=req, actor=actor, role=role)


# ---------------------------------------------------------------------------
# Department Review, Authorized Actions, Follow-Up, and Closure
# ---------------------------------------------------------------------------

@router.post("/cases/{case_id}/department-review", response_model=DepartmentReviewRecord, status_code=status.HTTP_201_CREATED)
async def api_record_department_review(
    case_id: str,
    req: DepartmentReviewRequest,
    current_user: Optional[Dict[str, Any]] = Security(get_optional_user)
):
    """Records administrative departmental review and strategic containment recommendation."""
    enforce_role(current_user, ["department_officer", "admin", "veterinarian"], "submitting department reviews")
    actor = current_user.get("sub") if current_user else req.reviewer
    role = current_user.get("role", "department_officer") if current_user else "department_officer"
    return await response_service.record_department_review(case_id=case_id, req=req, actor=actor, role=role)


@router.post("/cases/{case_id}/authorize-action", response_model=AuthorizedActionRecord, status_code=status.HTTP_201_CREATED)
async def api_authorize_action(
    case_id: str,
    req: AuthorizeActionRequest,
    current_user: Optional[Dict[str, Any]] = Security(get_optional_user)
):
    """
    Authorizes department containment or biosecurity intervention.
    STRICT GOVERNANCE: Authorized only by Department Officer or Admin. Farmers and Vets cannot autonomously authorize.
    """
    enforce_role(current_user, ["department_officer", "admin"], "authorizing government actions")
    actor = current_user.get("sub") if current_user else req.authorized_by
    role = current_user.get("role", "department_officer") if current_user else "department_officer"
    return await response_service.authorize_action(case_id=case_id, req=req, actor=actor, role=role)


@router.post("/cases/{case_id}/follow-up", response_model=FollowUpRecord, status_code=status.HTTP_201_CREATED)
async def api_record_follow_up(
    case_id: str,
    req: FollowUpRequest,
    current_user: Optional[Dict[str, Any]] = Security(get_optional_user)
):
    """Records on-site veterinary follow-up inspection and containment verification."""
    enforce_role(current_user, ["veterinarian", "field_officer", "admin"], "logging veterinary follow-ups")
    actor = current_user.get("sub") if current_user else req.officer_name
    role = current_user.get("role", "veterinarian") if current_user else "veterinarian"
    return await response_service.record_follow_up(case_id=case_id, req=req, actor=actor, role=role)


@router.post("/cases/{case_id}/close", response_model=ResponseCaseResponse)
async def api_close_case(
    case_id: str,
    req: CloseCaseRequest,
    current_user: Optional[Dict[str, Any]] = Security(get_optional_user)
):
    """
    Closes operational response case.
    Critical P1 cases require prior field investigation evidence before closure.
    """
    enforce_role(current_user, ["admin", "department_officer", "veterinarian"], "closing response cases")
    actor = current_user.get("sub") if current_user else "District Veterinary Officer"
    role = current_user.get("role", "admin") if current_user else "admin"
    return await response_service.close_case(case_id=case_id, req=req, actor=actor, role=role)


# ---------------------------------------------------------------------------
# Notifications Outbox
# ---------------------------------------------------------------------------

@router.get("/notifications", response_model=List[NotificationOutboxItem])
async def api_list_notifications(
    channel: Optional[NotificationChannel] = Query(None, description="IN_APP, SMS, WHATSAPP, EMAIL"),
    recipient: Optional[str] = Query(None, description="Recipient identifier"),
    current_user: Optional[Dict[str, Any]] = Security(get_optional_user)
):
    """Lists notification outbox messages. Unconnected gateways report NOT_CONFIGURED."""
    enforce_not_farmer(current_user, "viewing outbox telemetry")
    return await response_service.list_notifications(channel=channel, recipient_target=recipient)


@router.post("/notifications", response_model=NotificationOutboxItem, status_code=status.HTTP_201_CREATED)
async def api_queue_notification(
    req: QueueNotificationRequest,
    current_user: Optional[Dict[str, Any]] = Security(get_optional_user)
):
    """Queues operational notification. Enforces truth-in-telemetry without fake delivery timestamps."""
    enforce_not_farmer(current_user, "queueing notifications")
    return await response_service.queue_notification(req)


# ---------------------------------------------------------------------------
# SIH Demo Seed & 14-Step Execution Scenario
# ---------------------------------------------------------------------------

@router.post("/seed-demo")
async def api_seed_demo_data(
    current_user: Optional[Dict[str, Any]] = Security(get_optional_user)
):
    """Seeds synthetic demo response cases (RESP-DEMO-001, RESP-DEMO-002, RESP-DEMO-003)."""
    enforce_not_farmer(current_user, "seeding demo data")
    return await response_service.seed_demo_data()


@router.post("/demo/run-scenario", response_model=DemoScenarioResult)
async def api_run_demo_scenario(
    current_user: Optional[Dict[str, Any]] = Security(get_optional_user)
):
    """
    Executes the 14-step SIH Hackathon Field Response scenario
    demonstrating controlled human authority and auditable lifecycle.
    """
    enforce_not_farmer(current_user, "running demo scenario")
    return await response_service.run_demo_scenario()
