"""
AniCare AI — Model Registry Data Models & Schemas
Defines formal lifecycle states, validation contracts, and promotion gates.
"""

from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class ModelStatus(str, Enum):
    EXPERIMENTAL = "EXPERIMENTAL"
    VALIDATION = "VALIDATION"
    SHADOW = "SHADOW"
    APPROVED = "APPROVED"
    PRODUCTION = "PRODUCTION"
    RETIRED = "RETIRED"
    REJECTED = "REJECTED"


class ModelFramework(str, Enum):
    ONNX = "onnx"
    PYTORCH = "pytorch"
    TENSORFLOW = "tensorflow"
    TFLITE = "tflite"


class ModelIntegrityResult(BaseModel):
    is_valid: bool
    model_id: str
    expected_sha256: str
    computed_sha256: str
    file_path: str
    file_size_bytes: int
    error_message: Optional[str] = None


class PromotionGateCheck(BaseModel):
    gate_name: str
    passed: bool
    threshold: Optional[str] = None
    actual_value: Optional[str] = None
    details: str


class PromotionGateResult(BaseModel):
    can_promote: bool
    target_status: ModelStatus
    checks: List[PromotionGateCheck]
    blocking_reasons: List[str] = Field(default_factory=list)


class ModelMetrics(BaseModel):
    sensitivity: Optional[float] = None
    specificity: Optional[float] = None
    precision: Optional[float] = None
    macro_f1: Optional[float] = None
    accuracy: Optional[float] = None
    roc_auc: Optional[float] = None
    pr_auc: Optional[float] = None
    ece: Optional[float] = None
    latency_ms: Optional[float] = None


class ModelMetadataItem(BaseModel):
    model_id: str
    version: str
    species: str = "bovine"
    condition: str = "lumpy_skin_disease_screening"
    framework: ModelFramework = ModelFramework.ONNX
    architecture: str = "EfficientNet-B0"
    input_size: str = "224x224"
    threshold: float = 0.50
    status: ModelStatus = ModelStatus.EXPERIMENTAL
    is_immutable: bool = False
    created_at: str
    approved_at: Optional[str] = None
    approved_by: Optional[str] = None
    approval_reason: Optional[str] = None
    promoted_at: Optional[str] = None
    promoted_by: Optional[str] = None
    retired_at: Optional[str] = None
    sha256: str
    weights_path: str
    training_dataset: str
    validation_dataset: str
    test_dataset: str
    test_metrics: Optional[ModelMetrics] = None
    description: Optional[str] = None
    notes: Optional[str] = None
    shadow_target: Optional[str] = None  # model_id this model shadows if in SHADOW mode


class ShadowComparisonItem(BaseModel):
    prediction_id: str
    timestamp: str
    animal_id: Optional[str] = None
    production_model_id: str
    production_prediction: str
    production_confidence: float
    shadow_model_id: str
    shadow_prediction: str
    shadow_confidence: float
    is_agreement: bool
    confidence_difference: float
    latency_difference_ms: float
