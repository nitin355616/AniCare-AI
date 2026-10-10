"""
AniCare AI — Geospatial Disease Intelligence & Risk Mapping Schemas
Milestone 12: Enterprise Geospatial Livestock Disease Surveillance,
Hotspot Prioritization, Spatial Spread Analysis, and Department Decision Support.
"""

from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


GEOSPATIAL_SAFETY_DISCLAIMER = (
    "Geospatial risk signals are intended for early-warning decision support. "
    "Disease outbreaks require field investigation and appropriate confirmatory "
    "veterinary/laboratory procedures."
)


class GeoRiskTier(str, Enum):
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class HotspotStatus(str, Enum):
    EMERGING = "EMERGING"
    ACTIVE = "ACTIVE"
    ESCALATING = "ESCALATING"
    DECLINING = "DECLINING"
    RESOLVED = "RESOLVED"


class HotspotPriority(str, Enum):
    P1_CRITICAL = "P1"
    P2_HIGH = "P2"
    P3_MODERATE = "P3"
    P4_MONITOR = "P4"


class AggregationLevel(str, Enum):
    VILLAGE = "village"
    BLOCK = "block"
    DISTRICT = "district"
    STATE = "state"


class LocationAccuracy(str, Enum):
    VILLAGE = "VILLAGE"
    BLOCK = "BLOCK"
    DISTRICT = "DISTRICT"
    ADMINISTRATIVE = "ADMINISTRATIVE"
    CENTROID = "CENTROID"


class LocationSource(str, Enum):
    USER_PROVIDED = "USER_PROVIDED"
    ADMINISTRATIVE_CENTROID = "ADMINISTRATIVE_CENTROID"
    GOVERNMENT_REGISTRY = "GOVERNMENT_REGISTRY"


class GeoLocation(BaseModel):
    """Privacy-safe administrative hierarchy and geographic coordinates."""
    state: str = Field(default="Gujarat", description="State or Union Territory")
    district: str = Field(default="LOCATION_UNKNOWN", description="Revenue District")
    block: str = Field(default="LOCATION_UNKNOWN", description="Tehsil / Taluka / Block")
    village: str = Field(default="LOCATION_UNKNOWN", description="Village or settlement name")
    latitude: Optional[float] = Field(None, description="Centroid latitude (never exact household GPS)")
    longitude: Optional[float] = Field(None, description="Centroid longitude (never exact household GPS)")
    location_accuracy: LocationAccuracy = Field(default=LocationAccuracy.ADMINISTRATIVE)
    location_source: LocationSource = Field(default=LocationSource.USER_PROVIDED)


class RiskDriver(BaseModel):
    """Transparent, explainable risk score factor."""
    factor: str
    contribution: float = Field(..., description="Points or percentage contributed to final score")
    description: str


class RiskScoreBreakdown(BaseModel):
    risk_score: int = Field(..., ge=0, le=100)
    risk_tier: GeoRiskTier
    drivers: List[RiskDriver]
    summary: str


class MapPointResponse(BaseModel):
    """Privacy-safe geographic entity point for map overlays."""
    point_id: str
    level: str = "village"
    name: str
    state: str
    district: str
    block: str
    village: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    risk_score: int
    risk_tier: GeoRiskTier
    priority: HotspotPriority
    hotspot_status: HotspotStatus
    condition_signal: str
    active_cases: int
    growth_7d_pct: Optional[float] = None
    growth_label: str
    affected_animals: int
    affected_herds: int
    last_updated: str
    is_demo: bool = False
    disclaimer: str = GEOSPATIAL_SAFETY_DISCLAIMER


class HotspotSummaryItem(BaseModel):
    hotspot_id: str
    state: str
    district: str
    block: str
    village: str
    condition_signal: str
    risk_score: int
    risk_tier: GeoRiskTier
    priority: HotspotPriority
    hotspot_status: HotspotStatus
    cases: int
    growth_7d: float
    growth_label: str
    affected_animals: int
    affected_herds: int
    recommended_action: str
    last_updated: str
    is_demo: bool = False


class HotspotListResponse(BaseModel):
    total: int
    critical_count: int
    high_count: int
    moderate_count: int
    items: List[HotspotSummaryItem]
    disclaimer: str = GEOSPATIAL_SAFETY_DISCLAIMER


class HotspotTimelineItem(BaseModel):
    day_label: str
    date_str: str
    case_count: int
    high_risk_count: int


class SpatialSpreadSignal(BaseModel):
    signal_status: str = Field(..., description="'SPREAD_SIGNAL_DETECTED' or 'NO_CLEAR_SPREAD_SIGNAL'")
    confidence: str = "MODERATE"
    origin_area: str
    destination_area: str
    distance_approx_km: Optional[float] = None
    temporal_lag_days: int = 0
    description: str


class HotspotDossierResponse(BaseModel):
    hotspot_id: str
    state: str
    district: str
    block: str
    village: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    condition_signal: str
    risk_score: int
    risk_tier: GeoRiskTier
    priority: HotspotPriority
    hotspot_status: HotspotStatus
    cases: int
    affected_animals: int
    affected_herds: int
    growth_7d: float
    growth_label: str
    drivers: List[RiskDriver]
    timeline: List[HotspotTimelineItem]
    spatial_spread: List[SpatialSpreadSignal]
    recommended_actions: List[str]
    linked_outbreak_event_id: Optional[str] = None
    audit_trail: List[Dict[str, Any]] = []
    last_updated: str
    is_demo: bool = False
    disclaimer: str = GEOSPATIAL_SAFETY_DISCLAIMER


class GeospatialOverviewResponse(BaseModel):
    total_areas_monitored: int
    high_risk_areas: int
    critical_areas: int
    emerging_hotspots: int
    escalating_hotspots: int
    total_active_signals: int
    total_cases_last_7d: int
    observation_window_days: int = 7
    last_recalculated_at: str
    disclaimer: str = GEOSPATIAL_SAFETY_DISCLAIMER


class TrendPointItem(BaseModel):
    period_label: str
    days: int
    active_cases: int
    growth_pct: float
    critical_hotspots: int
    high_hotspots: int


class GeospatialTrendsResponse(BaseModel):
    trends: List[TrendPointItem]
    disclaimer: str = GEOSPATIAL_SAFETY_DISCLAIMER


class GeospatialSpreadResponse(BaseModel):
    spread_patterns_detected: int
    active_spread_signals: List[SpatialSpreadSignal]
    disclaimer: str = GEOSPATIAL_SAFETY_DISCLAIMER


class RecalculateRiskRequest(BaseModel):
    window_days: int = Field(default=7, ge=1, le=60)
    force_refresh: bool = False


class RecalculateRiskResponse(BaseModel):
    status: str = "success"
    window_days: int
    areas_evaluated: int
    hotspots_generated: int
    timestamp: str
    recalculated_by: str
    disclaimer: str = GEOSPATIAL_SAFETY_DISCLAIMER
