"""
AniCare AI — Visual Error & False-Negative Taxonomy
Defines standardized clinical and computer-vision failure taxonomies
for false-negative lesion misclassifications and false-positive alarms.
Expanded in Milestone 7 to support the full 12-category Field Robustness Evaluation.
"""

from enum import Enum
from typing import Dict, Any, List
from pydantic import BaseModel, Field


class FailureCategory(str, Enum):
    """Evidence-based failure categories for animal vision triage in field conditions."""
    EARLY_SUBTLE_PAPULES = "EARLY_SUBTLE_PAPULES"
    DISTANT_WHOLE_ANIMAL_FRAMING = "DISTANT_WHOLE_ANIMAL_FRAMING"
    SMALL_LESION_AREA = "SMALL_LESION_AREA"
    MUD_DEBRIS_OBSTRUCTION = "MUD_DEBRIS_OBSTRUCTION"
    POOR_LIGHTING = "POOR_LIGHTING"
    OCCLUSION = "OCCLUSION"
    BACKGROUND_COMPLEXITY = "BACKGROUND_COMPLEXITY"
    IMAGE_QUALITY = "IMAGE_QUALITY"
    PARTIAL_BODY = "PARTIAL_BODY"
    MOTION_BLUR = "MOTION_BLUR"
    NON_STANDARD_CAMERA = "NON_STANDARD_CAMERA"
    UNKNOWN_FAILURE = "UNKNOWN_FAILURE"
    # Backward compatibility alias for Milestone 6 audit tests
    UNKNOWN_VISUAL_FAILURE = "UNKNOWN_VISUAL_FAILURE"
    # Ordinary test presentation without adverse environmental degradation
    UNCLASSIFIED_STANDARD_CASE = "UNCLASSIFIED_STANDARD_CASE"


class FailureAnalysisRecord(BaseModel):
    """Individual record auditing a misclassified animal specimen."""
    sample_id: str
    file_path: str
    true_class: str
    predicted_class: str
    predicted_confidence: float
    lsd_probability: float
    failure_category: FailureCategory
    observed_visual_characteristics: List[str]
    addressable_by_preprocessing: bool
    addressable_by_architecture: bool
    clinical_risk_mitigation: str
    limitations: str


FAILURE_CATEGORY_DESCRIPTIONS: Dict[FailureCategory, Dict[str, str]] = {
    FailureCategory.EARLY_SUBTLE_PAPULES: {
        "title": "Early / Subtle Papular Lesions",
        "clinical_basis": (
            "Pre-ulcerative stage of Capripoxvirus infection where dermal papules are flat (<10mm), "
            "non-necrotic, and lack characteristic central umbilication (sit-fasts). Visually blends "
            "with normal epidermal grain."
        ),
        "engineering_strategy": "Higher input resolution or local patch-level zoom."
    },
    FailureCategory.DISTANT_WHOLE_ANIMAL_FRAMING: {
        "title": "Distant Whole-Animal Framing",
        "clinical_basis": (
            "Camera capture from >3 meters standoff distance where entire animal silhouette is captured, "
            "subsampling individual nodular elevations below feature-discriminative threshold."
        ),
        "engineering_strategy": "Guided camera framing guidelines in UI; automated bounding box cropping."
    },
    FailureCategory.SMALL_LESION_AREA: {
        "title": "Small Lesion Area / High Background Ratio",
        "clinical_basis": (
            "Lesions occupy <5% of the total pixel field. Global pooling over the 224x224 feature map "
            "dilutes localized lesion activations."
        ),
        "engineering_strategy": "Multi-crop / sliding window tiled inference."
    },
    FailureCategory.MUD_DEBRIS_OBSTRUCTION: {
        "title": "Mud / Organic Soil Obstruction",
        "clinical_basis": (
            "Heavy dried mud, dung splatters, or pasture vegetation caked on flank or legs obscuring "
            "the skin surface."
        ),
        "engineering_strategy": "Farmer UX capture prompt requiring clean inspection site."
    },
    FailureCategory.POOR_LIGHTING: {
        "title": "Harsh Shadow or Underexposure",
        "clinical_basis": (
            "Extreme oblique shadows cast by barn structures or severe backlight obscuring dorsal dermal texture."
        ),
        "engineering_strategy": "Contrast stretching, adaptive histogram equalization, or illumination invariant augmentation."
    },
    FailureCategory.OCCLUSION: {
        "title": "Physical Occlusion",
        "clinical_basis": (
            "Fence rails, barn stanchions, or cohort animals partially obstructing the field of view."
        ),
        "engineering_strategy": "Multi-view capture protocol."
    },
    FailureCategory.BACKGROUND_COMPLEXITY: {
        "title": "High Clutter Barn/Pasture Background",
        "clinical_basis": (
            "Straw bedding, earthen mounds, or rough barn walls displaying textural frequencies mimicking nodular skin."
        ),
        "engineering_strategy": "Animal foreground segmentation or multi-scale feature pyramids."
    },
    FailureCategory.IMAGE_QUALITY: {
        "title": "Image Quality & Compression Degradation",
        "clinical_basis": (
            "Severe JPEG compression artifacts or low optical sensor resolution degrading high-frequency lesion boundaries."
        ),
        "engineering_strategy": "Automated resolution filtering and edge-gradient quality checks."
    },
    FailureCategory.PARTIAL_BODY: {
        "title": "Partial Body / Extreme Closeup Crop",
        "clinical_basis": (
            "Image cropped too tightly to a single anatomical region (e.g. muzzle or hock only) without sufficient cutaneous context."
        ),
        "engineering_strategy": "Anatomical landmark detection and framing guidance in mobile UI."
    },
    FailureCategory.MOTION_BLUR: {
        "title": "Animal Motion Blur",
        "clinical_basis": (
            "Restless animal movement during exposure causing motion smear and loss of high-frequency dermal textures."
        ),
        "engineering_strategy": "Real-time Laplacian blur detection prompt during capture."
    },
    FailureCategory.NON_STANDARD_CAMERA: {
        "title": "Non-Standard Camera Sensor / Optical Distortion",
        "clinical_basis": (
            "Fish-eye distortion, heavy barrel aberration, or extreme white balance color cast from non-standard cameras."
        ),
        "engineering_strategy": "Color constancy calibration and lens distortion correction."
    },
    FailureCategory.UNKNOWN_FAILURE: {
        "title": "Unknown / Insufficient Visual Evidence",
        "clinical_basis": (
            "Specimen where visual appearance appears typical but model fails without unambiguous visual artifact. "
            "No speculative cause asserted."
        ),
        "engineering_strategy": "Active learning triage for human expert re-labeling."
    },
    FailureCategory.UNKNOWN_VISUAL_FAILURE: {
        "title": "Unknown Visual Failure (Legacy Alias)",
        "clinical_basis": (
            "Specimen where visual appearance appears typical but model fails without unambiguous visual artifact. "
            "No speculative cause asserted."
        ),
        "engineering_strategy": "Active learning triage for human expert re-labeling."
    },
    FailureCategory.UNCLASSIFIED_STANDARD_CASE: {
        "title": "Unclassified Standard Case (Ordinary Presentation)",
        "clinical_basis": (
            "Standard clinical or field specimen without adverse environmental artifacts "
            "(normal lighting, standard framing, clear coat, standard mobile camera sensor)."
        ),
        "engineering_strategy": "Baseline standard single-crop inference pipeline."
    }
}
