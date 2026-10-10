from fastapi import APIRouter, status
from pydantic import BaseModel
from typing import List, Optional

from ai.config import ai_config
from ai.dataset.external.provenance import provenance_registry
from ai.dataset.external.permission_registry import PermissionState

router = APIRouter(prefix="/evaluation", tags=["Model Evaluation & Governance"])


class ExternalValidationStatusResponse(BaseModel):
    dataset_b_status: str
    permission_status: str
    candidate_sources: List[str]
    image_count: int
    validated_image_count: int
    external_validation_available: bool
    model_version: str
    threshold: float
    statement: str
    notes: str


@router.get(
    "/external/status",
    response_model=ExternalValidationStatusResponse,
    status_code=status.HTTP_200_OK,
    summary="Get legal and validation status of independent external benchmarks"
)
async def get_external_validation_status():
    """
    Returns legal governance and validation readiness of Dataset B.
    Adheres to scientific truthfulness: reports external_validation_available = false
    until formal inter-institutional Data Transfer Agreements are completed.
    Never exposes private contact credentials or internal keys.
    """
    candidates = provenance_registry.get_candidate_external_sources()
    candidate_names = [c.get("source_name", c.get("source_id")) for c in candidates]

    return ExternalValidationStatusResponse(
        dataset_b_status=PermissionState.PERMISSION_REQUIRED.value,
        permission_status=PermissionState.PERMISSION_REQUIRED.value,
        candidate_sources=candidate_names,
        image_count=0,
        validated_image_count=0,
        external_validation_available=False,
        model_version=ai_config.MODEL_VERSION,
        threshold=ai_config.OPERATING_THRESHOLD,
        statement="External validation pending due to lack of a legally verified independent dataset.",
        notes=(
            "Candidate sources (AAU Anand / ICAR-DFMD) are registered under PERMISSION_REQUIRED status. "
            "Zero production images ingested. Dataset A held-out benchmark remains the official baseline."
        )
    )
