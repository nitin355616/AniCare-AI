"""
AniCare AI — Geospatial Disease Intelligence & Risk Mapping Routes
Milestone 12: REST Endpoints for Geospatial Risk Overlays, Hotspot Prioritization,
Spatial Spread Analysis, and Department-Level Early Warning.
"""

from typing import Optional, Dict, Any, List
from fastapi import APIRouter, Query, status, Security, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.schemas.geospatial import (
    GeospatialOverviewResponse,
    MapPointResponse,
    HotspotListResponse,
    HotspotDossierResponse,
    GeospatialTrendsResponse,
    GeospatialSpreadResponse,
    RecalculateRiskRequest,
    RecalculateRiskResponse
)
from app.services.geospatial_service import geospatial_service
from app.utils.security import decode_access_token

router = APIRouter(prefix="/geospatial", tags=["Geospatial Disease Intelligence & Risk Mapping"])
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


def enforce_vet_or_admin(current_user: Optional[Dict[str, Any]], operation_name: str = "Government Risk Operations") -> None:
    """
    Enforces privacy and RBAC guard.
    Farmers are strictly prohibited (HTTP 403) from accessing government-level disease maps,
    cross-village hotspot catalogs, and department-level recalculation triggers.
    """
    if not current_user:
        return  # Allow open demo querying in non-authenticated lab setups

    role = current_user.get("role", "farmer")
    if role not in ["veterinarian", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access forbidden: User role '{role}' is not authorized for {operation_name}. Farmer accounts are restricted to own herd telemetry to safeguard livestock privacy."
        )


@router.get("/overview", response_model=GeospatialOverviewResponse)
async def api_get_geospatial_overview(
    days: int = Query(7, ge=1, le=60, description="Temporal window days"),
    current_user: Optional[Dict[str, Any]] = Security(get_optional_user)
):
    """
    Returns real-time geospatial surveillance KPIs:
    Total areas monitored, high-risk areas, critical hotspots, emerging hotspots, and active syndromic signals.
    """
    enforce_vet_or_admin(current_user, "Geospatial Intelligence Overview")
    return await geospatial_service.get_overview(days=days)


@router.get("/risk-map", response_model=List[MapPointResponse])
async def api_get_risk_map(
    level: str = Query("village", description="Aggregation level: village, block, district"),
    days: int = Query(7, ge=1, le=60, description="Observation temporal window in days"),
    condition: Optional[str] = Query(None, description="Optional condition filter (e.g. Lumpy Skin Disease)"),
    current_user: Optional[Dict[str, Any]] = Security(get_optional_user)
):
    """
    Retrieves privacy-safe geospatial points for map visualization.
    Exact household/farmer coordinates are NEVER exposed; coordinates represent village/block centroids.
    Farmers are blocked (HTTP 403) to prevent neighbor disease profiling.
    """
    enforce_vet_or_admin(current_user, "Geographic Risk Map")
    return await geospatial_service.get_risk_map(level=level, days=days, condition=condition)


@router.get("/hotspots", response_model=HotspotListResponse)
async def api_get_hotspots(
    tier: Optional[str] = Query(None, description="Filter by risk tier (LOW, MODERATE, HIGH, CRITICAL)"),
    priority: Optional[str] = Query(None, description="Filter by priority (P1, P2, P3, P4)"),
    status: Optional[str] = Query(None, description="Filter by status (EMERGING, ACTIVE, ESCALATING, DECLINING, RESOLVED)"),
    limit: int = Query(50, ge=1, le=200),
    skip: int = Query(0, ge=0),
    current_user: Optional[Dict[str, Any]] = Security(get_optional_user)
):
    """
    Retrieves prioritized geospatial hotspots across villages and blocks.
    Farmers are blocked (HTTP 403).
    """
    enforce_vet_or_admin(current_user, "Hotspot Priority List")
    return await geospatial_service.get_hotspots(
        tier=tier,
        priority=priority,
        status_filter=status,
        limit=limit,
        skip=skip
    )


@router.get("/hotspots/{hotspot_id}", response_model=HotspotDossierResponse)
async def api_get_hotspot_dossier(
    hotspot_id: str,
    current_user: Optional[Dict[str, Any]] = Security(get_optional_user)
):
    """
    Retrieves a comprehensive epidemiological and geospatial dossier for an identified hotspot.
    Includes explainable risk drivers, 7-day timeline, spatial spread assessment, and field action steps.
    """
    enforce_vet_or_admin(current_user, "Hotspot Dossier")
    return await geospatial_service.get_hotspot_by_id(hotspot_id)


@router.get("/trends", response_model=GeospatialTrendsResponse)
async def api_get_geospatial_trends(
    current_user: Optional[Dict[str, Any]] = Security(get_optional_user)
):
    """
    Returns time-series risk trends across 24h, 7d, 14d, and 30d observation windows.
    """
    enforce_vet_or_admin(current_user, "Geospatial Trends")
    return await geospatial_service.get_trends()


@router.get("/spread", response_model=GeospatialSpreadResponse)
async def api_get_spatial_spread_signals(
    current_user: Optional[Dict[str, Any]] = Security(get_optional_user)
):
    """
    Detects geographical progression patterns across adjacent settlements.
    Provides early warning without asserting unverified biological transmission.
    """
    enforce_vet_or_admin(current_user, "Spatial Spread Signals")
    return await geospatial_service.get_spatial_spread_signals()


@router.post("/recalculate", response_model=RecalculateRiskResponse)
async def api_recalculate_risk(
    body: RecalculateRiskRequest,
    current_user: Optional[Dict[str, Any]] = Security(get_optional_user)
):
    """
    Triggers server-side risk snapshot recalculation from all primary animal and veterinary signals.
    Farmers are strictly blocked (HTTP 403). Veterinarians and Admins are authorized.
    """
    enforce_vet_or_admin(current_user, "Risk Recalculation")
    return await geospatial_service.recalculate_risk(
        window_days=body.window_days,
        current_user=current_user
    )


@router.post("/seed-demo")
async def api_seed_demo_data(
    current_user: Optional[Dict[str, Any]] = Security(get_optional_user)
):
    """
    Seeds clearly-labeled synthetic SIH demo data for live judging presentations.
    """
    enforce_vet_or_admin(current_user, "Demo Cluster Seeding")
    return await geospatial_service.seed_demo_data()
