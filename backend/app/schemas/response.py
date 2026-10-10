"""
AniCare AI — Field Response, Alert Orchestration & Government Action Schemas
Milestone 13: Operational Workflow, Alert Engine, Investigation Tracking,
Sample/Lab Management, Department Authorizations, and Auditable Timeline.
"""

from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


SAFETY_DISCLAIMER = (
    "AI-generated risk signals support prioritization. Field investigation "
    "and authorized veterinary/department decisions remain human-controlled."
)


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class ResponsePriority(str, Enum):
    P1 = "P1"  # CRITICAL - high operational priority based on risk signals
    P2 = "P2"  # HIGH
    P3 = "P3"  # MODERATE
    P4 = "P4"  # MONITORING


class ResponseSeverity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ResponseStatus(str, Enum):
    RISK_DETECTED = "RISK_DETECTED"
    ALERT_GENERATED = "ALERT_GENERATED"
    ALERT_ACKNOWLEDGED = "ALERT_ACKNOWLEDGED"
    INVESTIGATION_ASSIGNED = "INVESTIGATION_ASSIGNED"
    FIELD_INVESTIGATION = "FIELD_INVESTIGATION"
    VETERINARY_ASSESSMENT = "VETERINARY_ASSESSMENT"
    SAMPLE_COLLECTION = "SAMPLE_COLLECTION"
    LAB_PENDING = "LAB_PENDING"
    LAB_RESULT_RECORDED = "LAB_RESULT_RECORDED"
    DEPARTMENT_REVIEW = "DEPARTMENT_REVIEW"
    ACTION_AUTHORIZED = "ACTION_AUTHORIZED"
    ACTION_IN_PROGRESS = "ACTION_IN_PROGRESS"
    FOLLOW_UP = "FOLLOW_UP"
    RESOLVED = "RESOLVED"
    CANCELLED = "CANCELLED"


class SourceType(str, Enum):
    GEOSPATIAL_HOTSPOT = "GEOSPATIAL_HOTSPOT"
    OUTBREAK_EVENT = "OUTBREAK_EVENT"
    CRITICAL_VETERINARY_CASE = "CRITICAL_VETERINARY_CASE"
    FARMER_REQUEST = "FARMER_REQUEST"
    MANUAL = "MANUAL"


class SampleType(str, Enum):
    SWAB = "SWAB"
    BLOOD = "BLOOD"
    SERUM = "SERUM"
    SCAB_TISSUE = "SCAB_TISSUE"
    MILK = "MILK"
    OTHER = "OTHER"


class SampleStatus(str, Enum):
    COLLECTED = "COLLECTED"
    TRANSPORTED = "TRANSPORTED"
    LAB_PENDING = "LAB_PENDING"
    PROCESSING = "PROCESSING"
    RESULT_AVAILABLE = "RESULT_AVAILABLE"
    REJECTED = "REJECTED"


class LabResultType(str, Enum):
    POSITIVE = "POSITIVE"
    NEGATIVE = "NEGATIVE"
    INCONCLUSIVE = "INCONCLUSIVE"
    INVALID = "INVALID"
    PENDING = "PENDING"


class DepartmentDecisionType(str, Enum):
    MONITOR = "MONITOR"
    FIELD_FOLLOW_UP = "FIELD_FOLLOW_UP"
    ADDITIONAL_INVESTIGATION = "ADDITIONAL_INVESTIGATION"
    BIOSECURITY_REVIEW = "BIOSECURITY_REVIEW"
    AUTHORIZED_CONTAINMENT = "AUTHORIZED_CONTAINMENT"
    OTHER_AUTHORIZED_ACTION = "OTHER_AUTHORIZED_ACTION"


class ActionType(str, Enum):
    BIOSECURITY_REVIEW = "BIOSECURITY_REVIEW"
    FIELD_RECHECK = "FIELD_RECHECK"
    ADDITIONAL_SAMPLING = "ADDITIONAL_SAMPLING"
    VETERINARY_VISIT = "VETERINARY_VISIT"
    AUTHORIZED_CONTAINMENT = "AUTHORIZED_CONTAINMENT"
    AUTHORIZED_VACCINATION_REVIEW = "AUTHORIZED_VACCINATION_REVIEW"
    FARMER_GUIDANCE = "FARMER_GUIDANCE"
    MONITORING = "MONITORING"


class ActionStatus(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    SUSPENDED = "SUSPENDED"


class ClosureReason(str, Enum):
    NO_FURTHER_SIGNAL = "NO_FURTHER_SIGNAL"
    FIELD_VERIFICATION_COMPLETED = "FIELD_VERIFICATION_COMPLETED"
    CASE_RESOLVED = "CASE_RESOLVED"
    FALSE_POSITIVE_SIGNAL = "FALSE_POSITIVE_SIGNAL"
    TRANSFERRED = "TRANSFERRED"
    DUPLICATE = "DUPLICATE"
    OTHER = "OTHER"


class NotificationChannel(str, Enum):
    IN_APP = "IN_APP"
    SMS = "SMS"
    WHATSAPP = "WHATSAPP"
    EMAIL = "EMAIL"
    VOICE = "VOICE"


class NotificationStatus(str, Enum):
    QUEUED = "QUEUED"
    SENDING = "SENDING"
    SENT = "SENT"
    DELIVERED = "DELIVERED"
    FAILED = "FAILED"
    NOT_CONFIGURED = "NOT_CONFIGURED"
    CANCELLED = "CANCELLED"


# ---------------------------------------------------------------------------
# Location & Auxiliary Schemas
# ---------------------------------------------------------------------------

class ResponseLocation(BaseModel):
    state: str = Field("Demo State", description="State name")
    district: str = Field("Demo District", description="District name")
    block: str = Field("Demo Block", description="Block / Taluka name")
    village: str = Field("Demo Village", description="Village name")
    latitude: Optional[float] = Field(None, description="Coarse centroid latitude")
    longitude: Optional[float] = Field(None, description="Coarse centroid longitude")


class AlertEscalationItem(BaseModel):
    from_priority: ResponsePriority
    to_priority: ResponsePriority
    reason: str
    timestamp: str
    actor: str


class EvidenceItem(BaseModel):
    evidence_id: str
    file_name: str
    file_type: str
    checksum: str
    file_size_bytes: int
    uploaded_by: str
    uploaded_at: str
    notes: Optional[str] = None
    file_url: Optional[str] = None


class TimelineEvent(BaseModel):
    event_id: str
    response_case_id: str
    event_type: str
    timestamp: str
    actor: str
    role: str
    description: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SlaMetrics(BaseModel):
    time_to_acknowledge_minutes: Optional[float] = None
    time_to_assign_minutes: Optional[float] = None
    time_to_field_visit_minutes: Optional[float] = None
    time_to_sample_minutes: Optional[float] = None
    time_to_lab_result_minutes: Optional[float] = None
    time_to_resolution_minutes: Optional[float] = None
    is_p1_ack_overdue: bool = False
    is_p1_investigation_overdue: bool = False


# ---------------------------------------------------------------------------
# Operational Entity Schemas
# ---------------------------------------------------------------------------

class ResponseAlertItem(BaseModel):
    alert_id: str
    response_case_id: str
    source_type: SourceType
    source_id: str
    alert_type: str
    priority: ResponsePriority
    severity: ResponseSeverity
    status: str = "ACTIVE"
    title: str
    message: str
    location: ResponseLocation
    condition_signal: str
    risk_score: float
    created_at: str
    acknowledged_at: Optional[str] = None
    acknowledged_by: Optional[str] = None
    acknowledgement_comment: Optional[str] = None
    escalation_history: List[AlertEscalationItem] = Field(default_factory=list)
    is_demo: bool = False


class FieldInvestigationRecord(BaseModel):
    investigation_id: str
    response_case_id: str
    visit_date: str
    officer_id: str
    officer_name: str
    animals_observed: int
    symptoms_observed: List[str]
    affected_animals: int
    herds_observed: int
    biosecurity_observations: str
    mortality: int = 0
    photos: List[str] = Field(default_factory=list)
    notes: Optional[str] = None
    evidence: List[EvidenceItem] = Field(default_factory=list)
    created_at: str
    idempotency_key: Optional[str] = None


class SampleRecord(BaseModel):
    sample_id: str
    response_case_id: str
    sample_type: SampleType
    collected_at: str
    collected_by: str
    collected_by_name: str
    purpose: str
    status: SampleStatus = SampleStatus.LAB_PENDING
    lab_reference: Optional[str] = None
    test_name: Optional[str] = None
    lab_result: Optional[LabResultType] = None
    result_date: Optional[str] = None
    reviewed_by: Optional[str] = None
    notes: Optional[str] = None
    idempotency_key: Optional[str] = None


class DepartmentReviewRecord(BaseModel):
    review_id: str
    response_case_id: str
    decision: DepartmentDecisionType
    reason: str
    reviewer: str
    reviewer_role: str
    reviewed_at: str


class AuthorizedActionRecord(BaseModel):
    action_id: str
    response_case_id: str
    action_type: ActionType
    reason: str
    authorized_by: str
    authorized_at: str
    status: ActionStatus = ActionStatus.PENDING
    due_date: Optional[str] = None
    completion_notes: Optional[str] = None
    completed_at: Optional[str] = None


class FollowUpRecord(BaseModel):
    follow_up_id: str
    response_case_id: str
    follow_up_date: str
    status: str
    officer_name: str
    new_observations: str
    new_case_count: int
    risk_change: str
    action_outcome: str
    created_at: str
    idempotency_key: Optional[str] = None


class ResponseCaseResponse(BaseModel):
    response_case_id: str
    source_type: SourceType
    source_id: str
    risk_score: float
    priority: ResponsePriority
    severity: ResponseSeverity
    status: ResponseStatus
    location: ResponseLocation
    condition_signal: str
    created_at: str
    updated_at: str
    assigned_to: Optional[str] = None
    assigned_officer_name: Optional[str] = None
    is_demo: bool = False
    disclaimer: str = SAFETY_DISCLAIMER
    alerts: List[ResponseAlertItem] = Field(default_factory=list)
    investigations: List[FieldInvestigationRecord] = Field(default_factory=list)
    samples: List[SampleRecord] = Field(default_factory=list)
    department_reviews: List[DepartmentReviewRecord] = Field(default_factory=list)
    actions: List[AuthorizedActionRecord] = Field(default_factory=list)
    follow_ups: List[FollowUpRecord] = Field(default_factory=list)
    timeline: List[TimelineEvent] = Field(default_factory=list)
    sla_metrics: SlaMetrics = Field(default_factory=SlaMetrics)


# ---------------------------------------------------------------------------
# Request Models
# ---------------------------------------------------------------------------

class CreateResponseCaseRequest(BaseModel):
    source_type: SourceType = SourceType.GEOSPATIAL_HOTSPOT
    source_id: str = Field(..., description="Source identifier e.g. GEO-DEMO-001 or OB-2026-001")
    risk_score: float = Field(..., ge=0, le=100)
    priority: Optional[ResponsePriority] = None
    location: Optional[ResponseLocation] = None
    condition_signal: str = Field("SUSPECTED_LSD", description="Suspected clinical condition")
    is_demo: bool = False


class AcknowledgeAlertRequest(BaseModel):
    comment: str = Field("Alert acknowledged by field veterinary authority.", description="Operational comment")
    actor: Optional[str] = None


class AssignInvestigationRequest(BaseModel):
    assigned_to: str = Field(..., description="Officer identifier")
    assigned_officer_name: str = Field(..., description="Full officer name")
    due_date: str = Field(..., description="Target completion timestamp")
    priority: Optional[ResponsePriority] = None
    instructions: str = Field("Conduct field veterinary assessment and herd check.", description="Directives")


class InvestigationCreateRequest(BaseModel):
    visit_date: Optional[str] = None
    officer_name: str = Field("Dr. Patel (Field Officer)", description="Officer performing inspection")
    animals_observed: int = Field(..., ge=1)
    symptoms_observed: List[str] = Field(default_factory=list)
    affected_animals: int = Field(..., ge=0)
    herds_observed: int = Field(1, ge=1)
    biosecurity_observations: str = Field("Standard farm enclosure, isolation advised.")
    mortality: int = Field(0, ge=0)
    notes: Optional[str] = None
    evidence: List[EvidenceItem] = Field(default_factory=list)
    idempotency_key: Optional[str] = None


class SampleCreateRequest(BaseModel):
    sample_type: SampleType = SampleType.SWAB
    purpose: str = Field("Veterinary diagnostic confirmatory investigation")
    collected_at: Optional[str] = None
    collected_by_name: str = Field("Field Inspector")
    idempotency_key: Optional[str] = None


class LabResultRecordRequest(BaseModel):
    result: LabResultType = Field(..., description="POSITIVE, NEGATIVE, INCONCLUSIVE, or INVALID")
    test_name: str = Field("Real-Time RT-PCR Assay", description="Lab assay performed")
    lab_reference: str = Field(..., description="Official laboratory reference accession")
    reviewer: str = Field("Dr. Sharma (State Diagnostic Lab)", description="Authorized lab pathologist")
    notes: Optional[str] = None


class DepartmentReviewRequest(BaseModel):
    decision: DepartmentDecisionType = Field(..., description="Department decision")
    reason: str = Field(..., description="Detailed clinical / operational rationale")
    reviewer: str = Field("Joint Director (Animal Husbandry)", description="Department officer name")


class AuthorizeActionRequest(BaseModel):
    action_type: ActionType = Field(..., description="Authorized department containment/biosecurity action")
    reason: str = Field(..., description="Regulatory justification")
    authorized_by: str = Field("District Animal Husbandry Officer", description="Authorizing official")
    due_date: Optional[str] = None


class FollowUpRequest(BaseModel):
    follow_up_date: Optional[str] = None
    officer_name: str = Field("Field Veterinary Officer")
    new_observations: str = Field("Clinical lesions regressing, isolation maintained.")
    new_case_count: int = Field(0, ge=0)
    risk_change: str = Field("DECLINING", description="Risk trend trajectory")
    action_outcome: str = Field("Biosecurity ring maintained, no secondary transmission.")
    idempotency_key: Optional[str] = None


class CloseCaseRequest(BaseModel):
    closure_reason: ClosureReason = Field(..., description="Reason for response closure")
    final_status: ResponseStatus = Field(ResponseStatus.RESOLVED, description="Terminal state")
    comment: str = Field(..., description="Closing officer remarks")


class EscalateAlertRequest(BaseModel):
    to_priority: ResponsePriority = Field(..., description="Target elevated priority")
    reason: str = Field(..., description="Operational reason for escalation")


# ---------------------------------------------------------------------------
# Notification Schemas
# ---------------------------------------------------------------------------

class NotificationOutboxItem(BaseModel):
    notification_id: str
    channel: NotificationChannel
    recipient_type: str = "AUTHORIZED_OFFICER"
    recipient_target: str
    template: str
    title: str
    message: str
    status: NotificationStatus
    provider: Optional[str] = None
    created_at: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class QueueNotificationRequest(BaseModel):
    channel: NotificationChannel = NotificationChannel.IN_APP
    recipient_type: str = "AUTHORIZED_OFFICER"
    recipient_target: str = "district_vet_officer"
    template: str = "CRITICAL_ALERT"
    title: str
    message: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# Top-level Response & Statistics Schemas
# ---------------------------------------------------------------------------

class ResponseCaseListResponse(BaseModel):
    total: int
    items: List[ResponseCaseResponse]
    disclaimer: str = SAFETY_DISCLAIMER


class ResponseStatsResponse(BaseModel):
    active_alerts: int
    p1_cases: int
    pending_investigations: int
    field_visits_today: int
    samples_awaiting_lab: int
    department_reviews: int
    overdue_actions: int
    resolved_cases: int
    disclaimer: str = SAFETY_DISCLAIMER


class DemoScenarioStep(BaseModel):
    step_number: int
    action: str
    status: str
    timestamp: str
    details: str


class DemoScenarioResult(BaseModel):
    case_id: str
    steps_completed: int
    final_status: str
    timeline_events_count: int
    steps: List[DemoScenarioStep]
    message: str
    disclaimer: str = SAFETY_DISCLAIMER
