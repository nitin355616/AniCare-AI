"""
AniCare AI — Model Registry Package
Provides immutable model versioning, cryptographic checksum verification,
lifecycle state management, and promotion gates.
"""

from .models import (
    ModelStatus,
    ModelFramework,
    ModelMetadataItem,
    PromotionGateResult,
    ModelIntegrityResult,
    ShadowComparisonItem
)
from .registry import ModelRegistry, model_registry

__all__ = [
    "ModelStatus",
    "ModelFramework",
    "ModelMetadataItem",
    "PromotionGateResult",
    "ModelIntegrityResult",
    "ShadowComparisonItem",
    "ModelRegistry",
    "model_registry"
]
