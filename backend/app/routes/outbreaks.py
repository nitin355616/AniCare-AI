"""
AniCare AI — Outbreak Intelligence & Syndromic Surveillance Routes
Milestone 9C: REST Endpoints for Outbreak Detection, Risk Tiers, Investigations, and Hotspots.
"""

from typing import Optional, Dict, Any
from fastapi import APIRouter, Query, status, Depends, Security, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.schemas.outbreak import (
    OutbreakEventResponse,
    OutbreakEventListResponse,
    OutbreakAssignRequest,
    OutbreakStatusUpdateRequest,
    InvestigationRecord,
    OutbreakScanRequest,
    OutbreakStatsResponse,
    OutbreakTrendsResponse,
    HotspotsResponse
)
from app.services.outbreak_service import outbreak_service
from app.utils.security import decode_access_token

router = APIRouter(prefix="/outbreaks", tags=["Outbreak Intelligence & Early Warning"])
security_optional = HTTPBearer(auto_error=False)


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security_optional)
) -> Optional[Dict[str, Any]]:
    """Extracts and decodes JWT credentials if supplied, returning None otherwise."""
    if not credentials:
        return None
    try:
        return decode_access_token(credentials.credentials)
    except Exception:
        return None


def enforce_vet_or_admin(current_user: Optional[Dict[str, Any]]) -> None:
    """Enforces that the caller is an authenticated Veterinarian or Admin. Farmers are rejected with 403."""
    if not current_user:
        return  # Allow unauthenticated demo calls in development if needed, but if authenticated:
    role = current_user.get("role", "farmer")
    if role not in ["veterinarian", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access forbidden: User role '{role}' is not authorized. Requires veterinarian or admin credentials."
        )


@router.get("/stats", response_model=OutbreakStatsResponse)
async def api_get_outbreak_stats():
    """
    Returns real-time aggregated outbreak surveillance KPIs:
    Active clusters, red alerts, surveillance alerts, affected animals, villages, and districts.
    """
    return await outbreak_service.get_outbreak_stats()


@router.get("/trends", response_model=OutbreakTrendsResponse)
async def api_get_outbreak_trends():
    """
    Returns 7-day, 14-day, and 30-day case trajectories, cluster escalations,
    and percentage growth metrics with division-by-zero protection.
    """
    return await outbreak_service.get_outbreak_trends()


@router.get("/hotspots", response_model=HotspotsResponse)
async def api_get_geographic_hotspots():
    """
    Aggregates caseload hierarchically across State -> District -> Block -> Village
    and returns ranked epidemiological priority hotspots (HOTSPOT_HIGH, MEDIUM, LOW).
    """
    return await outbreak_service.get_geographic_hotspots()


@router.get("", response_model=OutbreakEventListResponse)
async def api_get_outbreaks(
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status (DETECTED, UNDER_SURVEILLANCE, VETERINARY_INVESTIGATION, ACTION_RECOMMENDED, MONITORING, RESOLVED, FALSE_ALERT)"),
    risk_tier: Optional[str] = Query(None, description="Filter by tier (TIER_1_ROUTINE, TIER_2_SURVEILLANCE, TIER_3_RED_ALERT)"),
    district: Optional[str] = Query(None, description="Filter by revenue district name"),
    is_demo: Optional[bool] = Query(None, description="Filter by demo vs real production surveillance events"),
    limit: int = Query(200, ge=1, le=1000),
    skip: int = Query(0, ge=0)
):
    """
    Retrieves active disease cluster events and early warning dossiers with multi-criteria filtering.
    """
    return await outbreak_service.get_outbreaks(
        status_filter=status_filter,
        risk_tier=risk_tier,
        district=district,
        is_demo=is_demo,
        limit=limit,
        skip=skip
    )


@router.post("/scan", status_code=status.HTTP_200_OK)
async def api_scan_outbreaks(
    data: OutbreakScanRequest,
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """
    Triggers an automated sliding temporal window syndromic scan across livestock cases.
    Identifies spatial-temporal clusters, recalculates risk scores, and dispatches early warning alerts.
    Requires: Veterinarian or Admin. Farmers blocked with HTTP 403.
    """
    enforce_vet_or_admin(current_user)
    return await outbreak_service.scan_and_detect_outbreaks(
        window_days=data.window_days,
        district_filter=data.district,
        village_filter=data.village,
        current_user=current_user
    )


@router.post("/seed-demo", response_model=OutbreakEventResponse, status_code=status.HTTP_201_CREATED)
async def api_seed_demo_outbreak(
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """
    Seeds a controlled synthetic demo cluster (Village Demo-A, Anand, Gujarat) for SIH 2026 jury presentations.
    Tagged with is_demo: true and clear disclaimer text.
    Requires: Veterinarian or Admin. Farmers blocked with HTTP 403.
    """
    enforce_vet_or_admin(current_user)
    return await outbreak_service.seed_sih_demo_cluster()


@router.get("/{event_id}", response_model=OutbreakEventResponse)
async def api_get_outbreak(event_id: str):
    """
    Retrieves full outbreak event dossier including risk breakdown, affected animals,
    clinical investigation record, and chronological audit trail.
    """
    return await outbreak_service.get_outbreak_by_id(event_id)


@router.post("/{event_id}/assign", response_model=OutbreakEventResponse)
async def api_assign_officer(
    event_id: str,
    data: OutbreakAssignRequest,
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """
    Assigns an active outbreak event to a designated Veterinary Medical Officer.
    Transitions status to VETERINARY_INVESTIGATION and appends immutable audit trail.
    Requires: Veterinarian or Admin. Farmers blocked with HTTP 403.
    """
    enforce_vet_or_admin(current_user)
    return await outbreak_service.assign_veterinary_officer(
        event_id=event_id,
        officer_name=data.officer_name,
        current_user=current_user,
        notes=data.notes
    )


@router.put("/{event_id}/status", response_model=OutbreakEventResponse)
async def api_update_outbreak_status(
    event_id: str,
    data: OutbreakStatusUpdateRequest,
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """
    Updates the operational lifecycle status of an outbreak event.
    Supports transition to MONITORING, RESOLVED, or FALSE_ALERT.
    Requires: Veterinarian or Admin. Farmers blocked with HTTP 403.
    """
    enforce_vet_or_admin(current_user)
    return await outbreak_service.update_outbreak_status(
        event_id=event_id,
        new_status=data.new_status,
        current_user=current_user,
        notes=data.notes
    )


@router.post("/{event_id}/investigation", response_model=OutbreakEventResponse)
async def api_record_investigation(
    event_id: str,
    data: InvestigationRecord,
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """
    Records a certified clinical field inspection by an on-site Veterinary Officer.
    Documents physical examinations, lab test orders, containment measures, and farmer guidance.
    Transitions status to ACTION_RECOMMENDED and appends audit trail.
    Requires: Certified Veterinarian. Farmers blocked with HTTP 403.
    """
    enforce_vet_or_admin(current_user)
    return await outbreak_service.record_investigation(
        event_id=event_id,
        record=data,
        current_user=current_user
    )
