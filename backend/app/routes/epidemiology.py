from fastapi import APIRouter, status
from typing import Dict, Any

try:
    from ai.epidemiology.early_warning import early_warning_service
    from ai.inference.model_scope import model_scope_registry
except ImportError:
    from backend.ai.epidemiology.early_warning import early_warning_service
    from backend.ai.inference.model_scope import model_scope_registry

router = APIRouter(prefix="/epidemiology", tags=["Epidemiology & Early-Warning Intelligence"])


@router.get(
    "/clusters",
    status_code=status.HTTP_200_OK,
    summary="Get active spatial-temporal disease cluster signals"
)
async def get_active_disease_clusters() -> Dict[str, Any]:
    """
    Returns active spatial-temporal disease clusters and early-warning event signals.
    Synthesizes live assessments with clearly-labeled simulated demo clusters for SIH 2026.
    """
    return early_warning_service.get_dashboard_early_warning_feed()


@router.get(
    "/roadmap",
    status_code=status.HTTP_200_OK,
    summary="Get multi-species architectural model scope roadmap"
)
async def get_multi_species_roadmap() -> Dict[str, Any]:
    """
    Declares active validated model scopes (Cattle) and the future multi-species roadmap
    (Buffalo, Goat, Sheep, Pig, Poultry, Dog) under ethical veterinary AI standards.
    """
    return model_scope_registry.get_full_architecture_roadmap()
