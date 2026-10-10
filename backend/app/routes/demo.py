"""
AniCare AI — SIH National Demo & Jury Packaging Routes
Milestone 14: REST Endpoints for Demo Health, One-Click Seeding, Safe Reset, and Step Control.
"""

from typing import Optional, Dict, Any
from fastapi import APIRouter, status, Security, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.schemas.demo import (
    DemoHealthResponse,
    DemoSeedResponse,
    DemoResetResponse,
    DemoStateResponse
)
from app.services.demo_service import demo_service
from app.utils.security import decode_access_token

router = APIRouter(prefix="/demo", tags=["SIH National Demo & Jury Packaging"])
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


@router.get("/health", response_model=DemoHealthResponse)
async def api_get_demo_health():
    """
    Returns comprehensive pre-flight demo system health:
    Backend status, MongoDB connectivity, Production Model SHA-256 verification, and test metrics.
    """
    return await demo_service.check_health()


@router.post("/seed", response_model=DemoSeedResponse, status_code=status.HTTP_201_CREATED)
async def api_seed_demo_dataset(
    session_id: str = "SIH-DEMO-001",
    current_user: Optional[Dict[str, Any]] = Security(get_optional_user)
):
    """
    One-click synthetic demo dataset seed:
    Initializes demo animals, health signals, geospatial hotspot, and response case.
    Strictly isolated with is_demo = True.
    """
    return await demo_service.seed_demo(session_id=session_id)


@router.post("/reset", response_model=DemoResetResponse)
async def api_reset_demo_dataset(
    session_id: str = "SIH-DEMO-001",
    current_user: Optional[Dict[str, Any]] = Security(get_optional_user)
):
    """
    Safely purges synthetic demo records (is_demo: True).
    CRITICAL: Real operational livestock records remain strictly untouched!
    """
    return await demo_service.reset_demo(session_id=session_id)


@router.get("/state", response_model=DemoStateResponse)
async def api_get_demo_state(
    session_id: str = "SIH-DEMO-001"
):
    """Returns the current 10-stage walkthrough state for the SIH Jury presentation."""
    return await demo_service.get_state(session_id=session_id)


@router.post("/step/{step_id}", response_model=DemoStateResponse)
async def api_set_demo_step(
    step_id: int,
    session_id: str = "SIH-DEMO-001"
):
    """Advances or navigates the active walkthrough step (1 to 10)."""
    return await demo_service.advance_step(step_id=step_id, session_id=session_id)
