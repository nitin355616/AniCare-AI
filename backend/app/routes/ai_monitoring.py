"""
AniCare AI — AI Model Monitoring & Governance REST Routes
Exposes MLOps endpoints for telemetry inspection, drift detection,
model registry operations, and promotion gates.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.schemas.ai_monitoring import (
    AIMonitoringSummaryResponse,
    PredictionEventItem,
    PredictionTelemetryResponse,
    AIFeedbackResponse,
    ModelRegisterRequest,
    ModelApproveRequest,
    ModelPromoteRequest,
    ModelRollbackRequest,
    DriftSimulateRequest
)
from app.services.ai_monitoring_service import ai_monitoring_service
from app.routes.veterinary import get_optional_user


try:
    from ai.experiments import experiment_tracker
    from ai.model_registry import ModelMetadataItem
except ImportError:
    from backend.ai.experiments import experiment_tracker
    from backend.ai.model_registry import ModelMetadataItem

router = APIRouter(prefix="/ai-monitoring", tags=["AI Model Monitoring & MLOps"])


@router.get(
    "/summary",
    response_model=AIMonitoringSummaryResponse,
    summary="Get overall AI model monitoring health and MLOps metrics"
)
async def get_monitoring_summary():
    """Returns production model state, telemetry volumes, vet agreement rates, and drift summary."""
    return await ai_monitoring_service.get_summary()


@router.get(
    "/predictions",
    response_model=PredictionTelemetryResponse,
    summary="List recent AI screening prediction events"
)
async def get_prediction_events(
    limit: int = Query(50, ge=1, le=500),
    species: Optional[str] = Query(None),
    model_version: Optional[str] = Query(None)
):
    """Retrieves chronological AI screening events with latency, confidence, and quality diagnostics."""
    items = await ai_monitoring_service.get_recent_predictions(
        limit=limit,
        species=species,
        model_version=model_version
    )
    return PredictionTelemetryResponse(total_count=len(items), predictions=items)


@router.get(
    "/feedback",
    response_model=List[AIFeedbackResponse],
    summary="List veterinary clinical feedback events"
)
async def get_feedback_events(
    limit: int = Query(50, ge=1, le=500),
    feedback_type: Optional[str] = Query(None)
):
    """Returns clinical feedback submitted by certified veterinarians."""
    return await ai_monitoring_service.get_feedback_events(limit=limit, feedback_type=feedback_type)


@router.get(
    "/drift",
    summary="Get statistical drift report across prediction distributions"
)
async def get_drift_report():
    """Calculates Population Stability Index (PSI) comparing recent telemetry against Dataset A baseline."""
    report = await ai_monitoring_service.get_drift_report()
    return report.model_dump()


@router.post(
    "/drift/simulate-demo",
    summary="Simulate controlled distribution shift for SIH hackathon demonstration"
)
async def simulate_demo_drift(payload: DriftSimulateRequest):
    """
    Sets simulated confidence/lighting shift (WATCH, WARNING, or CRITICAL)
    demonstrating that drift alerts trigger without changing the frozen production model.
    """
    return ai_monitoring_service.set_demo_drift_simulation(
        active=payload.simulate_shift,
        target_status=payload.target_status
    )


@router.get(
    "/models",
    summary="List registered models in model registry"
)
async def list_registered_models(
    species: Optional[str] = Query(None)
):
    """Returns catalog of models across all lifecycle states."""
    models = ai_monitoring_service.list_models()
    if species:
        models = [m for m in models if m.species.lower() == species.lower()]
    return [m.model_dump() for m in models]


@router.get(
    "/models/{model_id}",
    summary="Get details of a specific registered model"
)
async def get_model_details(model_id: str):
    """Returns model manifest, evaluation benchmarks, and promotion gate status."""
    model = ai_monitoring_service.get_model(model_id)
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Model '{model_id}' was not found in registry."
        )
    return model.model_dump()


@router.post(
    "/models/register",
    status_code=status.HTTP_201_CREATED,
    summary="Register a new experimental model manifest"
)
async def register_model(
    payload: ModelRegisterRequest,
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """Admin-only registration of new candidate model with cryptographic verification."""
    model = await ai_monitoring_service.register_model(payload, current_user=current_user)
    return model.model_dump()


@router.post(
    "/models/{model_id}/approve",
    summary="Approve model for deployment following validation gate evaluation"
)
async def approve_model(
    model_id: str,
    payload: ModelApproveRequest,
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """Admin-only action approving a model once pre-promotion safety gates pass."""
    model = await ai_monitoring_service.approve_model(model_id, payload, current_user=current_user)
    return model.model_dump()


@router.post(
    "/models/{model_id}/promote",
    summary="Promote APPROVED model to PRODUCTION"
)
async def promote_model_to_production(
    model_id: str,
    payload: ModelPromoteRequest,
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """Admin-only promotion to PRODUCTION, retiring previous production model."""
    model = await ai_monitoring_service.promote_model(model_id, payload, current_user=current_user)
    return model.model_dump()


@router.post(
    "/models/rollback",
    summary="Rollback PRODUCTION model to a previously approved version"
)
async def rollback_production_model(
    payload: ModelRollbackRequest,
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """Admin-only rollback action requiring SHA-256 integrity verification before activation."""
    model = await ai_monitoring_service.rollback_model(payload, current_user=current_user)
    return model.model_dump()


@router.post(
    "/verify-integrity",
    summary="Verify cryptographic SHA-256 checksum of production model on disk"
)
async def verify_integrity(model_id: Optional[str] = Query(None)):
    """Verifies physical file exists and hashes match manifest."""
    return ai_monitoring_service.verify_integrity(model_id=model_id)


@router.get(
    "/experiments",
    summary="List tracked continuous learning experiments"
)
async def list_experiments():
    """Returns history of training and augmentation experiments."""
    exps = experiment_tracker.list_experiments()
    return [e.model_dump() for e in exps]


@router.get(
    "/experiments/comparison",
    summary="Side-by-side benchmark comparison between Production V1 and Candidate V2"
)
async def get_experiment_comparison(
    baseline_id: str = Query("anicare_vision_bovine_v1"),
    candidate_id: str = Query("anicare_vision_bovine_v2")
):
    """Generates comparison matrix across recall, specificity, F1, AUC, and calibration."""
    comp = experiment_tracker.get_model_comparison(baseline_id=baseline_id, candidate_id=candidate_id)
    return comp.model_dump()


@router.get(
    "/data-quality",
    summary="Get dataset curation pipeline quality and provenance statistics"
)
async def get_data_quality_stats():
    """Returns breakdown of candidate samples, duplicate quarantine rates, and legal licensing status."""
    return {
        "verified_samples_count": 18,
        "pending_review_count": 6,
        "quarantined_duplicates_count": 3,
        "quarantined_poor_quality_count": 2,
        "dataset_b_quarantine_status": "PERMISSION_REQUIRED",
        "dataset_b_message": "Dataset B remains legally quarantined per institutional ethics guidelines pending executed Data Transfer Agreement.",
        "species_distribution": {
            "Cattle (Bovine)": 24,
            "Buffalo": 3,
            "Goat": 2
        },
        "evidence_tiers": {
            "LAB_CONFIRMED": 5,
            "VET_REVIEWED": 19,
            "UNVERIFIED": 5
        }
    }
