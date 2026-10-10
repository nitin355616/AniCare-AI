"""
AniCare AI — Dataset Intelligence Package
Exports data schema, quality checkers, manifest validators, and partitioning utilities.
"""

from .schema import (
    TargetSpeciesEnum,
    DiseaseCategoryEnum,
    DatasetSplitEnum,
    ImageQualityEnum,
    AnnotationStatusEnum,
    VETERINARY_TAXONOMY,
    DatasetManifestRecord,
)
from .quality import (
    ImageQualityChecker,
    ImageQualityAssessment,
    SUPPORTED_IMAGE_FORMATS,
    NEAR_DUPLICATE_HAMMING_THRESHOLD,
)
from .validator import (
    DatasetManifestValidator,
    UNVERIFIED_LICENSES,
)
from .manifest import (
    DatasetManifestManager,
)

__all__ = [
    "TargetSpeciesEnum",
    "DiseaseCategoryEnum",
    "DatasetSplitEnum",
    "ImageQualityEnum",
    "AnnotationStatusEnum",
    "VETERINARY_TAXONOMY",
    "DatasetManifestRecord",
    "ImageQualityChecker",
    "ImageQualityAssessment",
    "SUPPORTED_IMAGE_FORMATS",
    "NEAR_DUPLICATE_HAMMING_THRESHOLD",
    "DatasetManifestValidator",
    "UNVERIFIED_LICENSES",
    "DatasetManifestManager",
]
