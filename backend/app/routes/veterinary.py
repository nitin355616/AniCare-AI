from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Query, status, Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.schemas.veterinary import (
    VeterinaryCaseResponse,
    CaseCreateRequest,
    CaseReviewRequest,
    CaseTreatmentRequest,
    CaseFollowUpRequest,
    CaseCloseRequest,
    VeterinaryStatsResponse,
    CasePreventionRequest,
    CaseWithdrawalRequest
)
from app.services.veterinary_service import (
    get_veterinary_cases,
    get_case_by_id,
    create_veterinary_case,
    review_veterinary_case,
    add_case_treatment,
    schedule_case_follow_up,
    close_veterinary_case,
    get_veterinary_stats,
    update_case_prevention,
    update_case_withdrawal
)
from app.utils.security import decode_access_token

router = APIRouter(prefix="/veterinary", tags=["Veterinary Clinical Care"])
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

@router.get("/stats", response_model=VeterinaryStatsResponse)
async def api_get_stats():
    """
    Returns real-time aggregated veterinary case statistics from MongoDB.
    Counts pending reviews, high/critical risk cases, active treatments, follow-ups,
    vaccinations due, and withdrawal restrictions.
    """
    return await get_veterinary_stats()

@router.get("/cases", response_model=List[VeterinaryCaseResponse])
async def api_get_cases(
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by case status"),
    risk_filter: Optional[str] = Query(None, alias="risk", description="Filter by risk level"),
    animal_id: Optional[str] = Query(None, description="Filter by animal ID"),
    limit: int = Query(50, ge=1, le=200),
    skip: int = Query(0, ge=0)
):
    """
    Lists veterinary cases with optional risk, status, and animal ID filtering.
    """
    return await get_veterinary_cases(
        status_filter=status_filter,
        risk_filter=risk_filter,
        animal_id=animal_id,
        limit=limit,
        skip=skip
    )

@router.post("/cases", response_model=VeterinaryCaseResponse, status_code=status.HTTP_201_CREATED)
async def api_create_case(
    data: CaseCreateRequest,
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """
    Creates a new veterinary clinical case from AI screening or triage escalation.
    Initial status: PENDING_REVIEW.
    """
    return await create_veterinary_case(data, current_user=current_user)

@router.get("/cases/{case_id}", response_model=VeterinaryCaseResponse)
async def api_get_case(case_id: str):
    """
    Retrieves complete veterinary case file including AI assessment history, clinical review,
    approved treatments, prevention plan, and withdrawal restrictions.
    """
    return await get_case_by_id(case_id)

@router.put("/cases/{case_id}/review", response_model=VeterinaryCaseResponse)
async def api_review_case(
    case_id: str,
    data: CaseReviewRequest,
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """
    Veterinary Medical Officer review and clinical validation.
    Updates decision, clinical notes, and transitions status: PENDING_REVIEW -> REVIEWED.
    Enforces role restriction: Farmers are forbidden from clinical reviews.
    """
    return await review_veterinary_case(case_id, data, current_user=current_user)

@router.post("/cases/{case_id}/treatment", response_model=VeterinaryCaseResponse, status_code=status.HTTP_201_CREATED)
async def api_add_treatment(
    case_id: str,
    data: CaseTreatmentRequest,
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """
    Prescribes approved medication, dosage, supportive care, and optional withdrawal info.
    Transitions status: REVIEWED -> TREATMENT_ACTIVE.
    Requires certified veterinary medical license. Farmers and non-vet administrators are forbidden.
    """
    return await add_case_treatment(case_id, data, current_user=current_user)

@router.put("/cases/{case_id}/prevention", response_model=VeterinaryCaseResponse)
async def api_update_prevention(
    case_id: str,
    data: CasePreventionRequest,
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """
    Updates biosecurity quarantine, vector control, hygiene, and farmer instructions for a case.
    Restricted to authorized Veterinary Medical Officers.
    """
    return await update_case_prevention(case_id, data, current_user=current_user)

@router.put("/cases/{case_id}/withdrawal", response_model=VeterinaryCaseResponse)
async def api_update_withdrawal(
    case_id: str,
    data: CaseWithdrawalRequest,
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """
    Updates statutory food-safety withdrawal restrictions (milk and meat withholding periods).
    Restricted to authorized Veterinary Medical Officers.
    """
    return await update_case_withdrawal(case_id, data, current_user=current_user)

@router.post("/cases/{case_id}/follow-up", response_model=VeterinaryCaseResponse)
@router.put("/cases/{case_id}/follow-up", response_model=VeterinaryCaseResponse)
async def api_schedule_follow_up(
    case_id: str,
    data: CaseFollowUpRequest,
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """
    Schedules a clinical follow-up examination date and notes.
    Transitions status: TREATMENT_ACTIVE -> FOLLOW_UP.
    """
    return await schedule_case_follow_up(case_id, data, current_user=current_user)

@router.put("/cases/{case_id}/close", response_model=VeterinaryCaseResponse)
async def api_close_case(
    case_id: str,
    data: CaseCloseRequest,
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """
    Formally closes an active veterinary case after follow-up or recovery.
    Transitions status: FOLLOW_UP -> CLOSED.
    """
    return await close_veterinary_case(case_id, data, current_user=current_user)
