"""
AniCare AI — Veterinary AI Feedback REST Route
Enforces role-based clinical feedback recording.
Farmers are forbidden from clinical review (HTTP 403).
"""

from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.ai_monitoring import (
    AIFeedbackCreateRequest,
    AIFeedbackResponse
)
from app.services.ai_monitoring_service import ai_monitoring_service
from app.routes.veterinary import get_optional_user

router = APIRouter(prefix="/ai-feedback", tags=["Veterinary AI Feedback"])


@router.post(
    "",
    response_model=AIFeedbackResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit structured veterinary feedback on an AI prediction"
)
async def submit_veterinary_feedback(
    payload: AIFeedbackCreateRequest,
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """
    Certified Veterinarians and Admins record ground-truth validation:
    AI_ACCEPTED, AI_MODIFIED, AI_REJECTED, FURTHER_EXAMINATION, LAB_CONFIRMATION_REQUIRED, INSUFFICIENT_IMAGE.
    Farmers are forbidden (HTTP 403).
    """
    return await ai_monitoring_service.record_feedback(payload, current_user=current_user)
