from typing import Optional, Dict, Any
from fastapi import APIRouter, status, Depends
from app.schemas.farmer import (
    FarmerDashboardResponse,
    FarmerAnimalDetail,
    FarmerReviewRequest,
    FarmerReviewResponse,
    FarmerOutbreakWarning
)
from app.services.farmer_service import (
    get_farmer_dashboard,
    get_farmer_animal_detail,
    request_animal_review
)
from app.routes.veterinary import get_optional_user

router = APIRouter(prefix="/farmer", tags=["Farmer Experience & Low-Literacy Portal"])

@router.get("/dashboard", response_model=FarmerDashboardResponse)
async def api_get_farmer_dashboard(
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """
    Returns simplified, low-literacy dashboard for the requesting farmer.
    Respects ownership privacy and provides non-technical health statuses.
    """
    return await get_farmer_dashboard(current_user=current_user)

@router.get("/animals/{animal_id}", response_model=FarmerAnimalDetail)
async def api_get_farmer_animal_detail(
    animal_id: str,
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """
    Returns complete, simplified health dossier for a specific animal.
    Enforces privacy guard: returns HTTP 403 Forbidden if unowned by the requesting farmer.
    """
    return await get_farmer_animal_detail(animal_id=animal_id, current_user=current_user)

@router.post("/animals/{animal_id}/request-review", response_model=FarmerReviewResponse)
async def api_request_farmer_review(
    animal_id: str,
    request_data: FarmerReviewRequest,
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """
    Allows a farmer to request an immediate veterinary officer clinical visit.
    Enforces privacy guard: returns HTTP 403 Forbidden if unowned.
    """
    return await request_animal_review(animal_id=animal_id, request_data=request_data, current_user=current_user)

@router.get("/outbreak-warning", response_model=FarmerOutbreakWarning)
async def api_get_farmer_outbreak_warning(
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """
    Returns localized, non-alarmist public health advisory for the farmer's area.
    """
    dashboard = await get_farmer_dashboard(current_user=current_user)
    return dashboard.outbreak_warning
