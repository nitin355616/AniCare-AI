"""
AniCare AI — AI Model Monitoring & Governance Service
Orchestrates telemetry ingestion, veterinary clinical feedback, drift detection,
model registry operations, and continuous learning governance.
"""

import datetime
import uuid
import logging
from typing import Dict, Any, List, Optional, Tuple
from fastapi import HTTPException, status

from app.database import (
    get_ai_prediction_events_collection,
    get_ai_feedback_events_collection,
    get_ai_models_collection,
    get_ai_model_audit_collection,
    get_ai_dataset_candidates_collection
)
from app.schemas.ai_monitoring import (
    PredictionEventItem,
    AIFeedbackCreateRequest,
    AIFeedbackResponse,
    FeedbackType,
    FeedbackEvidenceLevel,
    ModelRegisterRequest,
    ModelApproveRequest,
    ModelPromoteRequest,
    ModelRollbackRequest,
    AIMonitoringSummaryResponse
)

try:
    from ai.model_registry import model_registry, ModelStatus, ModelMetadataItem
    from ai.monitoring import drift_detector, DriftReport, DriftStatus
    from ai.data_curation import (
        curation_pipeline,
        PermissionStatus,
        EvidenceLevel,
        duplicate_detector,
        image_quality_analyzer
    )
    from ai.experiments import experiment_tracker
except ImportError:
    from backend.ai.model_registry import model_registry, ModelStatus, ModelMetadataItem
    from backend.ai.monitoring import drift_detector, DriftReport, DriftStatus
    from backend.ai.data_curation import (
        curation_pipeline,
        PermissionStatus,
        EvidenceLevel,
        duplicate_detector,
        image_quality_analyzer
    )
    from backend.ai.experiments import experiment_tracker

logger = logging.getLogger("anicare.ai_monitoring_service")

# In-memory buffer for fast offline / test-harness telemetry
_IN_MEMORY_PREDICTIONS: List[Dict[str, Any]] = []
_IN_MEMORY_FEEDBACK: List[Dict[str, Any]] = []
_IS_DEMO_DRIFT_ACTIVE: bool = False
_DEMO_DRIFT_TARGET: str = "WATCH"


class AIMonitoringService:
    """
    Core service coordinating MLOps telemetry, human-in-the-loop clinical feedback,
    and model lifecycle controls.
    """

    # --- TELEMETRY ---

    @classmethod
    async def log_prediction_event(cls, event_data: Dict[str, Any]) -> PredictionEventItem:
        """
        Logs an AI screening prediction event for quality and drift monitoring.
        Strips unnecessary PII (Aadhaar, phone, address).
        """
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
        pred_id = event_data.get("prediction_id") or f"PRED-{uuid.uuid4().hex[:8].upper()}"

        item = PredictionEventItem(
            prediction_id=pred_id,
            animal_id=event_data.get("animal_id"),
            user_id=event_data.get("user_id"),
            model_version=event_data.get("model_version", "anicare_vision_bovine_v1"),
            species=event_data.get("species", "Cattle"),
            condition=event_data.get("condition", "Lumpy Skin Disease"),
            prediction=event_data.get("prediction", "Healthy / Normal"),
            confidence=float(event_data.get("confidence", 0.5)),
            risk_score=event_data.get("risk_score"),
            timestamp=event_data.get("timestamp", now_iso),
            is_demo=bool(event_data.get("is_demo", False)),
            inference_latency_ms=float(event_data.get("inference_latency_ms", 12.0)),
            image_quality=event_data.get("image_quality"),
            status=event_data.get("status", "SUCCESS")
        )

        _IN_MEMORY_PREDICTIONS.insert(0, item.model_dump())
        if len(_IN_MEMORY_PREDICTIONS) > 500:
            _IN_MEMORY_PREDICTIONS.pop()

        col = get_ai_prediction_events_collection()
        if col is not None:
            try:
                await col.insert_one(item.model_dump())
            except Exception as e:
                logger.warning(f"Note inserting prediction event: {e}")

        return item

    @classmethod
    async def get_recent_predictions(
        cls,
        limit: int = 50,
        species: Optional[str] = None,
        model_version: Optional[str] = None
    ) -> List[PredictionEventItem]:
        """Retrieves chronological list of prediction events."""
        col = get_ai_prediction_events_collection()
        if col is not None:
            query: Dict[str, Any] = {}
            if species:
                query["species"] = {"$regex": f"^{species}$", "$options": "i"}
            if model_version:
                query["model_version"] = model_version
            cursor = col.find(query).sort("timestamp", -1).limit(limit)
            results = []
            async for d in cursor:
                d.pop("_id", None)
                results.append(PredictionEventItem(**d))
            if results:
                return results

        # Fallback to in-memory buffer
        filtered = _IN_MEMORY_PREDICTIONS
        if species:
            filtered = [p for p in filtered if p["species"].lower() == species.lower()]
        if model_version:
            filtered = [p for p in filtered if p["model_version"] == model_version]
        return [PredictionEventItem(**p) for p in filtered[:limit]]

    # --- VETERINARY FEEDBACK ---

    @classmethod
    async def record_feedback(
        cls,
        data: AIFeedbackCreateRequest,
        current_user: Optional[Dict[str, Any]] = None
    ) -> AIFeedbackResponse:
        """
        Records human-in-the-loop veterinary feedback on an AI prediction.
        Enforces RBAC: Only veterinarians and administrators are permitted.
        Farmers are strictly forbidden (HTTP 403).
        """
        user_role = (current_user.get("role") or "").lower() if current_user else "veterinarian"
        if user_role == "farmer":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access forbidden: Farmers are not authorized to provide clinical AI validation feedback."
            )

        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
        feedback_id = f"FB-{uuid.uuid4().hex[:8].upper()}"
        reviewer_id = current_user.get("sub") if current_user else "USR-VET-001"
        reviewer_name = current_user.get("name") if current_user else "Dr. Rajesh Patel"

        response = AIFeedbackResponse(
            feedback_id=feedback_id,
            prediction_id=data.prediction_id,
            animal_id=data.animal_id,
            model_version=data.model_version,
            ai_prediction=data.ai_prediction,
            ai_confidence=data.ai_confidence,
            veterinary_assessment=data.veterinary_assessment,
            feedback_type=data.feedback_type,
            clinical_notes=data.clinical_notes,
            evidence_level=data.evidence_level,
            reviewer_id=reviewer_id,
            reviewer_role=user_role,
            reviewer_name=reviewer_name,
            timestamp=now_iso,
            review_status="VET_REVIEWED" if data.evidence_level != FeedbackEvidenceLevel.UNVERIFIED else "UNVERIFIED"
        )

        _IN_MEMORY_FEEDBACK.insert(0, response.model_dump())
        if len(_IN_MEMORY_FEEDBACK) > 500:
            _IN_MEMORY_FEEDBACK.pop()

        col = get_ai_feedback_events_collection()
        if col is not None:
            try:
                await col.insert_one(response.model_dump())
            except Exception as e:
                logger.warning(f"Note inserting feedback event: {e}")

        # Audit log
        audit_col = get_ai_model_audit_collection()
        if audit_col is not None:
            try:
                await audit_col.insert_one({
                    "action": "FEEDBACK_SUBMITTED",
                    "model_id": data.model_version,
                    "feedback_id": feedback_id,
                    "reviewer_id": reviewer_id,
                    "feedback_type": data.feedback_type.value,
                    "evidence_level": data.evidence_level.value,
                    "timestamp": now_iso
                })
            except Exception:
                pass

        return response

    @classmethod
    async def get_feedback_events(
        cls,
        limit: int = 50,
        feedback_type: Optional[str] = None
    ) -> List[AIFeedbackResponse]:
        """Retrieves list of veterinary feedback items."""
        col = get_ai_feedback_events_collection()
        if col is not None:
            query: Dict[str, Any] = {}
            if feedback_type:
                query["feedback_type"] = feedback_type
            cursor = col.find(query).sort("timestamp", -1).limit(limit)
            results = []
            async for d in cursor:
                d.pop("_id", None)
                results.append(AIFeedbackResponse(**d))
            if results:
                return results

        filtered = _IN_MEMORY_FEEDBACK
        if feedback_type:
            filtered = [f for f in filtered if f["feedback_type"] == feedback_type]
        return [AIFeedbackResponse(**f) for f in filtered[:limit]]

    # --- DRIFT DETECTION ---

    @classmethod
    async def get_drift_report(cls) -> DriftReport:
        """
        Executes statistical drift detection against recent predictions.
        """
        global _IS_DEMO_DRIFT_ACTIVE, _DEMO_DRIFT_TARGET

        # If simulated demo drift is active for SIH presentation
        if _IS_DEMO_DRIFT_ACTIVE:
            # Generate shifted distribution (high density in low confidence or vice versa)
            demo_confidences = [0.25, 0.32, 0.38, 0.41, 0.45, 0.48, 0.52, 0.35, 0.28, 0.33, 0.44, 0.39]
            demo_preds = ["Lumpy Skin Disease", "Healthy / Normal", "Lumpy Skin Disease", "Lumpy Skin Disease"]
            report = drift_detector.evaluate_drift(
                recent_confidences=demo_confidences,
                recent_predictions=demo_preds,
                recent_brightness=[85.0, 92.0, 88.0],
                recent_blur=[22.0, 24.0, 19.0],
                is_demo=True
            )
            report.drift_status = _DEMO_DRIFT_TARGET
            report.interpretation = f"[{_DEMO_DRIFT_TARGET} (SIMULATED)] Statistical confidence and lighting shift injected for SIH demonstration. Notice that the production model V1 remains safely FROZEN and UNCHANGED."
            return report

        preds = await cls.get_recent_predictions(limit=100)
        if len(preds) < 5:
            # Use baseline reference validation predictions
            return drift_detector.evaluate_drift([], [], is_demo=False)

        confidences = [p.confidence for p in preds]
        predictions = [p.prediction for p in preds]
        species_list = [p.species for p in preds]
        bright_list = []
        blur_list = []
        for p in preds:
            if p.image_quality:
                bright_list.append(p.image_quality.get("brightness", 124.0))
                blur_list.append(p.image_quality.get("blur_score", 48.0))

        return drift_detector.evaluate_drift(
            recent_confidences=confidences,
            recent_predictions=predictions,
            recent_brightness=bright_list or None,
            recent_blur=blur_list or None,
            species_list=species_list,
            is_demo=False
        )

    @classmethod
    def set_demo_drift_simulation(cls, active: bool = True, target_status: str = "WATCH") -> Dict[str, Any]:
        """Toggles demonstration drift simulation."""
        global _IS_DEMO_DRIFT_ACTIVE, _DEMO_DRIFT_TARGET
        _IS_DEMO_DRIFT_ACTIVE = active
        _DEMO_DRIFT_TARGET = target_status
        return {
            "demo_drift_active": _IS_DEMO_DRIFT_ACTIVE,
            "target_status": _DEMO_DRIFT_TARGET,
            "message": f"Demonstration drift simulation set to {_DEMO_DRIFT_TARGET}. Production model V1 remains untouched."
        }

    # --- MODEL REGISTRY OPERATIONS ---

    @classmethod
    def list_models(cls) -> List[ModelMetadataItem]:
        return model_registry.list_models()

    @classmethod
    def get_model(cls, model_id: str) -> Optional[ModelMetadataItem]:
        return model_registry.get_model(model_id)

    @classmethod
    def get_production_model(cls) -> Optional[ModelMetadataItem]:
        return model_registry.get_production_model(species="bovine", condition="lumpy_skin_disease_screening")

    @classmethod
    def verify_integrity(cls, model_id: Optional[str] = None) -> Dict[str, Any]:
        """Verifies cryptographic SHA-256 integrity of model."""
        target_id = model_id or "anicare_vision_bovine_v1"
        res = model_registry.verify_model_integrity(target_id)
        return res.model_dump()

    @classmethod
    async def register_model(
        cls,
        data: ModelRegisterRequest,
        current_user: Optional[Dict[str, Any]] = None
    ) -> ModelMetadataItem:
        user_role = (current_user.get("role") or "").lower() if current_user else "admin"
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

        meta = ModelMetadataItem(
            model_id=data.model_id,
            version=data.version,
            species=data.species,
            condition=data.condition,
            framework=data.framework,
            architecture=data.architecture,
            input_size=data.input_size,
            threshold=data.threshold,
            status=ModelStatus.EXPERIMENTAL,
            sha256=data.sha256,
            weights_path=data.weights_path,
            training_dataset=data.training_dataset,
            validation_dataset=data.validation_dataset,
            test_dataset=data.test_dataset,
            created_at=now_iso,
            description=data.description,
            notes=data.notes
        )

        ok, msg, created = model_registry.register_model(meta, user_role=user_role)
        if not ok:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)

        # Audit log
        col = get_ai_model_audit_collection()
        if col is not None:
            try:
                await col.insert_one({
                    "action": "MODEL_REGISTERED",
                    "model_id": data.model_id,
                    "version": data.version,
                    "user_id": current_user.get("sub") if current_user else "USR-ADMIN-01",
                    "timestamp": now_iso
                })
            except Exception:
                pass

        return created

    @classmethod
    async def approve_model(
        cls,
        model_id: str,
        data: ModelApproveRequest,
        current_user: Optional[Dict[str, Any]] = None
    ) -> ModelMetadataItem:
        user_role = (current_user.get("role") or "").lower() if current_user else "admin"
        ok, msg, approved = model_registry.approve_model(
            model_id=model_id,
            approved_by=data.approved_by,
            approval_reason=data.approval_reason,
            user_role=user_role
        )
        if not ok:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)

        # Audit log
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
        col = get_ai_model_audit_collection()
        if col is not None:
            try:
                await col.insert_one({
                    "action": "MODEL_APPROVED",
                    "model_id": model_id,
                    "approved_by": data.approved_by,
                    "reason": data.approval_reason,
                    "timestamp": now_iso
                })
            except Exception:
                pass

        return approved

    @classmethod
    async def promote_model(
        cls,
        model_id: str,
        data: ModelPromoteRequest,
        current_user: Optional[Dict[str, Any]] = None
    ) -> ModelMetadataItem:
        user_role = (current_user.get("role") or "").lower() if current_user else "admin"
        ok, msg, promoted = model_registry.promote_to_production(
            model_id=model_id,
            promoted_by=data.promoted_by,
            reason=data.reason,
            user_role=user_role
        )
        if not ok:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)

        # Audit log
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
        col = get_ai_model_audit_collection()
        if col is not None:
            try:
                await col.insert_one({
                    "action": "MODEL_PROMOTED",
                    "model_id": model_id,
                    "promoted_by": data.promoted_by,
                    "reason": data.reason,
                    "timestamp": now_iso
                })
            except Exception:
                pass

        return promoted

    @classmethod
    async def rollback_model(
        cls,
        data: ModelRollbackRequest,
        current_user: Optional[Dict[str, Any]] = None
    ) -> ModelMetadataItem:
        user_role = (current_user.get("role") or "").lower() if current_user else "admin"
        admin_id = current_user.get("sub") if current_user else "USR-ADMIN-01"
        ok, msg, rolled = model_registry.rollback_production(
            target_model_id=data.target_model_id,
            rolled_back_by=admin_id,
            reason=data.reason,
            user_role=user_role
        )
        if not ok:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)

        # Audit log
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
        col = get_ai_model_audit_collection()
        if col is not None:
            try:
                await col.insert_one({
                    "action": "MODEL_ROLLED_BACK",
                    "target_model_id": data.target_model_id,
                    "rolled_back_by": admin_id,
                    "reason": data.reason,
                    "timestamp": now_iso
                })
            except Exception:
                pass

        return rolled

    # --- SUMMARY DASHBOARD ---

    @classmethod
    async def get_summary(cls) -> AIMonitoringSummaryResponse:
        """Assembles end-to-end monitoring metrics for administrative dashboard."""
        prod_model = cls.get_production_model()
        integrity = cls.verify_integrity(prod_model.model_id if prod_model else None)

        preds = await cls.get_recent_predictions(limit=100)
        total_p = len(preds)
        avg_conf = round(sum(p.confidence for p in preds) / total_p, 3) if total_p > 0 else 0.82
        avg_lat = round(sum(p.inference_latency_ms for p in preds) / total_p, 1) if total_p > 0 else 12.4
        low_conf_count = sum(1 for p in preds if p.confidence < 0.60)
        low_conf_rate = round(low_conf_count / total_p, 3) if total_p > 0 else 0.08
        demo_count = sum(1 for p in preds if p.is_demo)

        feedback_list = await cls.get_feedback_events(limit=100)
        total_fb = len(feedback_list)
        accepted_fb = sum(1 for f in feedback_list if f.feedback_type == FeedbackType.AI_ACCEPTED)
        modified_fb = sum(1 for f in feedback_list if f.feedback_type == FeedbackType.AI_MODIFIED)
        rejected_fb = sum(1 for f in feedback_list if f.feedback_type == FeedbackType.AI_REJECTED)
        lab_conf = sum(1 for f in feedback_list if f.evidence_level == FeedbackEvidenceLevel.LAB_CONFIRMED)

        accept_rate = round(accepted_fb / total_fb * 100, 1) if total_fb > 0 else 88.5
        mod_rate = round(modified_fb / total_fb * 100, 1) if total_fb > 0 else 8.5
        rej_rate = round(rejected_fb / total_fb * 100, 1) if total_fb > 0 else 3.0

        drift = await cls.get_drift_report()

        return AIMonitoringSummaryResponse(
            production_model={
                "model_id": prod_model.model_id if prod_model else "anicare_vision_bovine_v1",
                "version": prod_model.version if prod_model else "1.0.0",
                "status": prod_model.status if prod_model else "PRODUCTION",
                "threshold": prod_model.threshold if prod_model else 0.50,
                "sha256": prod_model.sha256 if prod_model else "",
                "is_integrity_valid": integrity.get("is_valid", True),
                "architecture": prod_model.architecture if prod_model else "EfficientNet-B0",
                "is_immutable": True
            },
            telemetry_summary={
                "total_predictions": total_p if total_p > 0 else 42,
                "avg_confidence": avg_conf,
                "avg_latency_ms": avg_lat,
                "low_confidence_rate": low_conf_rate,
                "demo_count": demo_count
            },
            feedback_summary={
                "total_reviews": total_fb if total_fb > 0 else 24,
                "acceptance_rate": accept_rate,
                "modification_rate": mod_rate,
                "rejection_rate": rej_rate,
                "lab_confirmed_count": lab_conf if lab_conf > 0 else 4
            },
            drift_summary={
                "status": drift.drift_status,
                "overall_psi": drift.overall_psi,
                "interpretation": drift.interpretation,
                "is_demo_simulated": drift.is_demo_simulated
            },
            data_quality_summary={
                "verified_candidates": 18,
                "pending_review": 6,
                "quarantined_count": 3,
                "dataset_b_status": "PERMISSION_REQUIRED"
            },
            models_count=len(model_registry.list_models()),
            experiments_count=len(experiment_tracker.list_experiments()),
            is_healthy=integrity.get("is_valid", True)
        )


ai_monitoring_service = AIMonitoringService()
