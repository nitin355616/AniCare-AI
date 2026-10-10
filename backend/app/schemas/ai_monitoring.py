"""
AniCare AI — AI Model Monitoring & Governance Schemas
Data contracts for MLOps telemetry, veterinary feedback, drift reports,
and model lifecycle operations.
"""

from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class FeedbackType(str, Enum):
    AI_ACCEPTED = "AI_ACCEPTED"
    AI_MODIFIED = "AI_MODIFIED"
    AI_REJECTED = "AI_REJECTED"
    FURTHER_EXAMINATION = "FURTHER_EXAMINATION"
    LAB_CONFIRMATION_REQUIRED = "LAB_CONFIRMATION_REQUIRED"
    INSUFFICIENT_IMAGE = "INSUFFICIENT_IMAGE"


class FeedbackEvidenceLevel(str, Enum):
    UNVERIFIED = "UNVERIFIED"
    VET_REVIEWED = "VET_REVIEWED"
    LAB_CONFIRMED = "LAB_CONFIRMED"
    REJECTED = "REJECTED"


class PredictionEventItem(BaseModel):
    prediction_id: str
    animal_id: Optional[str] = None
    user_id: Optional[str] = None
    model_version: str
    species: str
    condition: str
    prediction: str
    confidence: float
    risk_score: Optional[float] = None
    timestamp: str
    is_demo: bool = False
    inference_latency_ms: float
    image_quality: Optional[Dict[str, Any]] = None
    status: str = "SUCCESS"


class PredictionTelemetryResponse(BaseModel):
    total_count: int
    predictions: List[PredictionEventItem]


class AIFeedbackCreateRequest(BaseModel):
    prediction_id: str
    animal_id: Optional[str] = None
    model_version: str
    ai_prediction: str
    ai_confidence: float
    veterinary_assessment: str
    feedback_type: FeedbackType
    clinical_notes: Optional[str] = None
    evidence_level: FeedbackEvidenceLevel = FeedbackEvidenceLevel.VET_REVIEWED
    lab_test_name: Optional[str] = None
    lab_test_result: Optional[str] = None


class AIFeedbackResponse(BaseModel):
    feedback_id: str
    prediction_id: str
    animal_id: Optional[str] = None
    model_version: str
    ai_prediction: str
    ai_confidence: float
    veterinary_assessment: str
    feedback_type: FeedbackType
    clinical_notes: Optional[str] = None
    evidence_level: FeedbackEvidenceLevel
    reviewer_id: str
    reviewer_role: str
    reviewer_name: Optional[str] = None
    timestamp: str
    review_status: str


class ModelRegisterRequest(BaseModel):
    model_id: str
    version: str
    species: str = "bovine"
    condition: str = "lumpy_skin_disease_screening"
    framework: str = "onnx"
    architecture: str = "EfficientNet-B0"
    input_size: str = "224x224"
    threshold: float = 0.50
    sha256: str
    weights_path: str
    training_dataset: str
    validation_dataset: str
    test_dataset: str
    test_metrics: Optional[Dict[str, float]] = None
    description: Optional[str] = None
    notes: Optional[str] = None


class ModelApproveRequest(BaseModel):
    approved_by: str
    approval_reason: str


class ModelPromoteRequest(BaseModel):
    promoted_by: str
    reason: str


class ModelRollbackRequest(BaseModel):
    target_model_id: str
    reason: str


class DriftSimulateRequest(BaseModel):
    simulate_shift: bool = True
    target_status: str = "WATCH"  # "WATCH" | "WARNING" | "CRITICAL"


class AIMonitoringSummaryResponse(BaseModel):
    production_model: Dict[str, Any]
    telemetry_summary: Dict[str, Any]
    feedback_summary: Dict[str, Any]
    drift_summary: Dict[str, Any]
    data_quality_summary: Dict[str, Any]
    models_count: int
    experiments_count: int
    is_healthy: bool
