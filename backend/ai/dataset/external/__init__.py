"""
AniCare AI — External Dataset Ingestion, Validation & Benchmark Package
Milestone 8A
"""

from ai.dataset.external.permission_registry import (
    PermissionState,
    PermissionRegistry,
    LegalEthicalGate
)
from ai.dataset.external.provenance import (
    ExternalSourceProvenance,
    ExternalProvenanceRegistry,
    provenance_registry
)
from ai.dataset.external.external_manifest import (
    ExternalManifestRecord,
    ExternalDatasetManifest
)
from ai.dataset.external.duplicate_guard import (
    ExternalDuplicateGuard,
    duplicate_guard
)
from ai.dataset.external.label_audit import (
    EvidenceLevel,
    ExternalLabelAuditor,
    label_auditor
)
from ai.dataset.external.quality_audit import (
    QualityTier,
    ExternalQualityAuditor,
    quality_auditor
)
from ai.dataset.external.grouping import (
    AnimalGroupingAuditor,
    grouping_auditor
)
from ai.dataset.external.validator import (
    ExternalDatasetValidator,
    external_dataset_validator
)
from ai.dataset.external.evaluator import (
    ExternalModelEvaluator,
    external_evaluator,
    wilson_score_interval
)

__all__ = [
    "PermissionState",
    "PermissionRegistry",
    "LegalEthicalGate",
    "ExternalSourceProvenance",
    "ExternalProvenanceRegistry",
    "provenance_registry",
    "ExternalManifestRecord",
    "ExternalDatasetManifest",
    "ExternalDuplicateGuard",
    "duplicate_guard",
    "EvidenceLevel",
    "ExternalLabelAuditor",
    "label_auditor",
    "QualityTier",
    "ExternalQualityAuditor",
    "quality_auditor",
    "AnimalGroupingAuditor",
    "grouping_auditor",
    "ExternalDatasetValidator",
    "external_dataset_validator",
    "ExternalModelEvaluator",
    "external_evaluator",
    "wilson_score_interval"
]
