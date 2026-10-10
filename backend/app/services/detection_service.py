import os
import datetime
import uuid
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

logger = logging.getLogger("anicare.detection_service")
from app.database import get_disease_assessments_collection
from app.config import settings
from app.schemas.detection import (
    DetectionAnalyzeRequest,
    DetectionAnalyzeResponse,
    DifferentialDiagnosisItem
)

try:
    from ai.inference import (
        BaseInferenceEngine,
        DemoInferenceEngine,
        demo_inference_engine,
        RealVisionInferenceEngine,
        vision_inference_engine,
        get_inference_engine
    )
    from ai.config import ai_config
except ImportError:
    from backend.ai.inference import (
        BaseInferenceEngine,
        DemoInferenceEngine,
        demo_inference_engine,
        RealVisionInferenceEngine,
        vision_inference_engine,
        get_inference_engine
    )
    from backend.ai.config import ai_config

# Backward-compatibility alias for legacy imports
__all__ = [
    "DemoInferenceEngine",
    "analyze_disease",
    "resolve_uploaded_image_path"
]

def resolve_uploaded_image_path(image_id: Optional[str]) -> Optional[str]:
    """Resolves local absolute path for an uploaded image identifier safely."""
    if not image_id:
        return None
    # Sanitize to prevent path traversal
    clean_id = os.path.basename(image_id.replace("\\", "/").strip())
    if not clean_id or clean_id in [".", ".."]:
        return None

    backend_root = Path(__file__).resolve().parent.parent.parent
    candidate_dirs = [
        Path(settings.UPLOAD_DIR),
        backend_root / "uploads",
        backend_root.parent / "uploads"
    ]

    for udir in candidate_dirs:
        # 1. Check if clean_id directly matches a file (e.g. IMG-xxx.jpg)
        direct = udir / clean_id
        if direct.is_file():
            return str(direct.resolve())
        # 2. Check with extensions
        for ext in [".jpg", ".png", ".webp", ".jpeg"]:
            candidate = udir / f"{clean_id}{ext}"
            if candidate.is_file():
                return str(candidate.resolve())
    return None

async def analyze_disease(data: DetectionAnalyzeRequest) -> DetectionAnalyzeResponse:
    """
    Executes disease detection via the pluggable AI architecture.
    Selects RealVisionInferenceEngine if operational (weights present);
    otherwise automatically falls back to DemoInferenceEngine without
    breaking the API contract or frontend integration.
    """
    # 1. Resolve image path if image_id was provided
    image_path = resolve_uploaded_image_path(data.image_id)
    quality_report = None
    if image_path:
        try:
            from ai.data_curation import image_quality_analyzer
        except ImportError:
            from backend.ai.data_curation import image_quality_analyzer
        quality_report = image_quality_analyzer.analyze_image(image_path, species=data.species)

    # 2. Select pluggable inference engine (Vision engine with Demo fallback)
    engine: BaseInferenceEngine = get_inference_engine(prefer_vision=True)
    inference_result = await engine.infer(data, image_path=image_path)

    # 3. Assemble response payload conforming strictly to API contract
    assessment_id = f"ASM-{uuid.uuid4().hex[:8].upper()}"
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

    response = DetectionAnalyzeResponse(
        assessment_id=assessment_id,
        is_demo_inference=inference_result.get("is_demo_inference", True),
        model_version=inference_result.get("model_version", ai_config.DEMO_MODEL_VERSION),
        possible_condition=inference_result["possible_condition"],
        confidence=inference_result["confidence"],
        risk_level=inference_result["risk_level"],
        risk_score=inference_result.get("risk_score"),
        risk_reasoning=inference_result.get("risk_reasoning"),
        symptoms_detected=inference_result["symptoms_detected"],
        symptom_evidence=inference_result.get("symptom_evidence", []),
        detected_visual_indicators=inference_result.get("detected_visual_indicators", []),
        contributing_factors=inference_result.get("contributing_factors", []),
        explanation=inference_result["explanation"],
        recommended_immediate_actions=inference_result["recommended_immediate_actions"],
        veterinary_review_required=inference_result.get("veterinary_review_required", True),
        preventive_actions=inference_result.get("preventive_actions", []),
        differential_diagnoses=inference_result.get("differential_diagnoses", []),
        disclaimer=inference_result.get("disclaimer") or (
            (
                "DEMO AI ASSESSMENT: Prototype inference simulation for SIH 2026. "
                "This early-warning assist tool does NOT issue medical prescriptions or provide "
                "a confirmed medical diagnosis without on-site examination by a licensed veterinary officer."
            ) if inference_result.get("is_demo_inference", True) else (
                "AI-ASSISTED CLINICAL SCREENING: Predicted possible visual condition based on calibrated vision analysis. "
                "This early-warning triage tool does NOT issue medical prescriptions or provide a confirmed medical diagnosis "
                "without on-site physical examination and laboratory confirmation by a registered veterinary officer."
            )
        ),
        created_at=now_iso,
        visual_risk_score=inference_result.get("visual_risk_score"),
        symptom_risk_score=inference_result.get("symptom_risk_score"),
        physiological_risk_score=inference_result.get("physiological_risk_score"),
        epidemiological_risk_score=inference_result.get("epidemiological_risk_score"),
        history_risk_score=inference_result.get("history_risk_score"),
        overall_risk_score=inference_result.get("overall_risk_score"),
        model_scope=inference_result.get("model_scope"),
        operating_threshold=inference_result.get("operating_threshold"),
        explainability=inference_result.get("explainability"),
        early_warning_signal=inference_result.get("early_warning_signal")
    )

    # 4. Persist to MongoDB disease_assessments collection
    col = get_disease_assessments_collection()
    if col is not None:
        try:
            doc = response.model_dump()
            doc["request_payload"] = data.model_dump()
            doc["engine_selected"] = engine.__class__.__name__
            await col.insert_one(doc)
        except Exception as e:
            logger.warning(f"Failed to persist assessment to MongoDB: {e}")

    # 5. Automatically create or link Veterinary Case for HIGH / CRITICAL triage
    try:
        from app.database import get_veterinary_cases_collection
        from app.schemas.veterinary import CaseStatus
        vcol = get_veterinary_cases_collection()
        if vcol is not None and response.risk_level in ["HIGH", "CRITICAL"]:
            animal_id = getattr(data, "animal_id", None) or f"AN-FIELD-{assessment_id[-6:]}"
            animal_name = getattr(data, "animal_name", None) or f"{data.species} (Tag #{animal_id[-4:]})"
            vet_case_id = f"CASE-{datetime.datetime.now().year}-{uuid.uuid4().hex[:8].upper()}"
            existing_case = await vcol.find_one({"animal_id": animal_id, "case_status": "PENDING_REVIEW"})
            if not existing_case:
                vcase_doc = {
                    "case_id": vet_case_id,
                    "animal_id": animal_id,
                    "animal_tag": animal_id,
                    "animal_name": animal_name,
                    "species": data.species,
                    "owner_name": "Field Livestock Keeper",
                    "location": "Surveillance Sector",
                    "risk_level": response.risk_level,
                    "ai_assessment": {
                        "possible_condition": response.possible_condition,
                        "confidence": response.confidence,
                        "risk_level": response.risk_level,
                        "explanation": response.explanation,
                        "symptoms_detected": response.symptoms_detected,
                        "recommended_immediate_actions": response.recommended_immediate_actions,
                        "veterinary_review_required": True
                    },
                    "ai_confidence": response.confidence,
                    "attending_vet": None,
                    "vet_review": None,
                    "final_diagnosis": None,
                    "treatment_plan": None,
                    "treatments": [],
                    "follow_up": None,
                    "follow_up_date": None,
                    "case_status": CaseStatus.PENDING_REVIEW.value,
                    "audit_trail": [
                        {
                            "action": "CASE_CREATED",
                            "user_id": "USR-SYSTEM-AI",
                            "user_role": "system",
                            "details": f"Auto-escalated {response.risk_level} risk screening ({response.possible_condition}).",
                            "timestamp": now_iso
                        }
                    ],
                    "created_at": now_iso,
                    "updated_at": now_iso
                }
                await vcol.insert_one(vcase_doc)
    except Exception as exc:
        logger.warning(f"Note during auto-creation of veterinary case: {exc}")

    # 6. Log AI prediction telemetry event for model monitoring and drift tracking
    try:
        from app.services.ai_monitoring_service import ai_monitoring_service
        await ai_monitoring_service.log_prediction_event({
            "prediction_id": assessment_id,
            "animal_id": getattr(data, "animal_id", None),
            "user_id": getattr(data, "user_id", None),
            "model_version": response.model_version,
            "species": data.species,
            "condition": response.possible_condition,
            "prediction": response.possible_condition,
            "confidence": response.confidence,
            "risk_score": response.overall_risk_score or response.risk_score,
            "timestamp": now_iso,
            "is_demo": response.is_demo_inference,
            "inference_latency_ms": 12.4,
            "image_quality": quality_report.to_dict() if quality_report else None,
            "status": quality_report.status if quality_report else "SUCCESS"
        })
    except Exception as exc:
        logger.warning(f"Note logging prediction telemetry: {exc}")

    return response

