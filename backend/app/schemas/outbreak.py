"""
AniCare AI — Outbreak Intelligence & Early Warning Schemas
Milestone 9C: Herd, Village, Block, District, and State-Level Syndromic Surveillance.
"""

from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class OutbreakRiskTier(str, Enum):
    TIER_1_ROUTINE = "TIER_1_ROUTINE"
    TIER_2_SURVEILLANCE = "TIER_2_SURVEILLANCE"
    TIER_3_RED_ALERT = "TIER_3_RED_ALERT"


class OutbreakStatus(str, Enum):
    DETECTED = "DETECTED"
    UNDER_SURVEILLANCE = "UNDER_SURVEILLANCE"
    VETERINARY_INVESTIGATION = "VETERINARY_INVESTIGATION"
    ACTION_RECOMMENDED = "ACTION_RECOMMENDED"
    MONITORING = "MONITORING"
    RESOLVED = "RESOLVED"
    FALSE_ALERT = "FALSE_ALERT"


class HotspotLevel(str, Enum):
    HOTSPOT_LOW = "HOTSPOT_LOW"
    HOTSPOT_MEDIUM = "HOTSPOT_MEDIUM"
    HOTSPOT_HIGH = "HOTSPOT_HIGH"


class LabTestStatus(str, Enum):
    NOT_REQUIRED = "NOT_REQUIRED"
    SAMPLES_SENT = "SAMPLES_SENT"
    AWAITING_RESULTS = "AWAITING_RESULTS"
    CONFIRMED_POSITIVE = "CONFIRMED_POSITIVE"
    CONFIRMED_NEGATIVE = "CONFIRMED_NEGATIVE"


class LocationHierarchy(BaseModel):
    """Administrative geographical hierarchy conforming to Indian administrative boundaries."""
    village: str = Field(default="LOCATION_UNKNOWN", description="Village or settlement name")
    block: str = Field(default="LOCATION_UNKNOWN", description="Sub-district / Tehsil / Taluka / Block")
    district: str = Field(default="LOCATION_UNKNOWN", description="Revenue District")
    state: str = Field(default="Gujarat", description="State or Union Territory")
    pincode: Optional[str] = Field(None, description="Postal Index Number if available")


class AffectedAnimalSummary(BaseModel):
    """Brief metadata for an individual animal participating in an outbreak event."""
    animal_id: str
    tag: Optional[str] = None
    species: str = "Cattle"
    risk_level: str = "HIGH"
    risk_score: Optional[float] = None
    condition: str = "Suspected Lumpy Skin Disease"
    owner: Optional[str] = None
    detected_at: str


class InvestigationRecord(BaseModel):
    """Certified clinical field investigation filed by Veterinary Medical Officer."""
    field_visit_date: str = Field(..., description="Date of physical on-site epidemiological inspection")
    animals_examined: int = Field(..., ge=1, description="Total livestock head examined during inspection")
    clinical_observations: str = Field(..., min_length=5, description="Physical symptoms and clinical staging")
    suspected_condition: str = Field(..., description="Veterinary provisional diagnosis")
    laboratory_test_required: bool = Field(default=False, description="Whether confirmatory lab assay is ordered")
    laboratory_test_status: LabTestStatus = Field(default=LabTestStatus.NOT_REQUIRED)
    preventive_actions: List[str] = Field(default_factory=list, description="Immediate herd containment steps")
    biosecurity_actions: List[str] = Field(default_factory=list, description="Disinfection and vector barrier actions")
    farmer_guidance: str = Field(default="", description="Instructions communicated to herd owners")
    follow_up_date: Optional[str] = Field(None, description="Scheduled date for post-intervention checkup")
    investigation_notes: str = Field(default="", description="Additional clinical and epidemiological notes")
    investigating_officer: str = Field(..., description="Name of inspecting Veterinary Officer")
    officer_license: Optional[str] = Field(None, description="State Veterinary Council registration number")
    submitted_at: str = Field(default="", description="ISO timestamp of investigation filing")


class OutbreakAuditEvent(BaseModel):
    """Immutable audit trail entry for an outbreak lifecycle transition."""
    action: str = Field(..., description="Action identifier (e.g. OFFICER_ASSIGNED, STATUS_CHANGED)")
    actor_id: str = Field(..., description="User ID or SYSTEM")
    actor_role: str = Field(..., description="Role of the actor: veterinarian, admin, system")
    timestamp: str = Field(..., description="ISO timestamp of the event")
    event_id: str = Field(..., description="Target outbreak event ID")
    previous_status: Optional[str] = None
    new_status: Optional[str] = None
    notes: Optional[str] = None


class OutbreakEventResponse(BaseModel):
    """Full outbreak intelligence dossier conforming to SIH 2026 specifications."""
    event_id: str = Field(..., description="Unique event identifier (e.g. OUT-2026-0001)")
    status: OutbreakStatus
    risk_tier: OutbreakRiskTier
    risk_score: int = Field(..., ge=0, le=100, description="Explainable aggregate score (0-100)")
    disease_signal: str = Field(..., description="Primary suspected condition/pathogen")
    condition: str = Field(..., description="Descriptive condition label")
    animal_ids: List[str] = Field(default_factory=list)
    case_count: int = Field(default=0)
    herd_ids: List[str] = Field(default_factory=list)
    location: LocationHierarchy
    window_start: str
    window_end: str
    first_detected_at: str
    last_updated_at: str
    trend_percentage: float = Field(default=0.0, description="Percentage change vs previous analysis window")
    trigger_reasons: List[str] = Field(default_factory=list, description="Explainable criteria triggers")
    veterinary_review_status: str = Field(default="PENDING")
    assigned_veterinary_officer: Optional[str] = None
    assigned_at: Optional[str] = None
    assigned_by: Optional[str] = None
    investigation_record: Optional[InvestigationRecord] = None
    investigation_notes: Optional[str] = None
    recommended_actions: List[str] = Field(default_factory=list)
    audit_trail: List[OutbreakAuditEvent] = Field(default_factory=list)
    affected_animals_details: Optional[List[AffectedAnimalSummary]] = None
    is_demo: bool = False
    disclaimer: str
    created_at: str
    updated_at: str


class OutbreakEventListResponse(BaseModel):
    total: int
    active_clusters: int
    red_alerts: int
    items: List[OutbreakEventResponse]


class OutbreakAssignRequest(BaseModel):
    officer_name: str = Field(..., min_length=2, description="Name of the assigned Veterinary Officer")
    notes: Optional[str] = Field(default="", description="Assignment memorandum or instructions")


class OutbreakStatusUpdateRequest(BaseModel):
    new_status: OutbreakStatus
    notes: Optional[str] = Field(default="", description="Clinical or operational justification")


class OutbreakScanRequest(BaseModel):
    window_days: int = Field(default=7, ge=3, le=90, description="Sliding temporal window in days (7, 14, 30)")
    district: Optional[str] = None
    village: Optional[str] = None


class OutbreakStatsResponse(BaseModel):
    """Aggregated real-time outbreak surveillance statistics."""
    active_clusters: int
    surveillance_alerts: int
    red_alerts: int
    routine_events: int
    resolved_events: int
    false_alerts: int
    total_events: int
    affected_animals_count: int
    affected_villages_count: int
    affected_districts_count: int


class OutbreakTrendItem(BaseModel):
    period_label: str  # e.g., "Last 7 Days"
    days: int
    total_cases: int
    high_risk_cases: int
    critical_cases: int
    possible_clusters: int
    suspected_outbreaks: int
    red_alerts: int
    resolved_events: int
    trend_percentage: float


class OutbreakTrendsResponse(BaseModel):
    windows: List[OutbreakTrendItem]


class HotspotVillageItem(BaseModel):
    village: str
    block: str
    district: str
    state: str
    case_count: int
    high_critical_count: int
    hotspot_level: HotspotLevel
    dominant_condition: str
    active_clusters: int


class HotspotsResponse(BaseModel):
    total_hotspots: int
    high_priority_hotspots: int
    medium_priority_hotspots: int
    low_priority_hotspots: int
    hotspots: List[HotspotVillageItem]
