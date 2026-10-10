"""
AniCare AI — Image Quality & Domain Diagnostics
Evaluates input image resolution, brightness, contrast, blur, and domain validity
prior to AI vision inference. Prevents diagnostic hallucinations on degraded or out-of-domain images.
"""

from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import numpy as np
from PIL import Image

try:
    from ai.inference.model_scope import model_scope_registry
except ImportError:
    from backend.ai.inference.model_scope import model_scope_registry


class ImageQualityReport:
    def __init__(
        self,
        is_sufficient: bool,
        quality_score: float,
        resolution: Tuple[int, int],
        brightness: float,
        contrast: float,
        blur_score: float,
        issues: List[str],
        status: str,
        message: str
    ):
        self.is_sufficient = is_sufficient
        self.quality_score = quality_score
        self.resolution = resolution
        self.brightness = brightness
        self.contrast = contrast
        self.blur_score = blur_score
        self.issues = issues
        self.status = status
        self.message = message

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_sufficient": self.is_sufficient,
            "quality_score": round(self.quality_score, 1),
            "resolution": {"width": self.resolution[0], "height": self.resolution[1]},
            "brightness": round(self.brightness, 1),
            "contrast": round(self.contrast, 1),
            "blur_score": round(self.blur_score, 2),
            "issues": self.issues,
            "status": self.status,
            "message": self.message
        }


class ImageQualityAnalyzer:
    """
    Analyzes raw livestock photos to detect common field degradation modes:
    - Extreme darkness / shadow
    - Blown-out flash / overexposure
    - Motion blur or defocus
    - Low resolution
    - Low contrast / washed out textures
    """

    MIN_WIDTH: int = 96
    MIN_HEIGHT: int = 96
    MIN_BRIGHTNESS: float = 20.0
    MAX_BRIGHTNESS: float = 235.0
    MIN_CONTRAST: float = 12.0
    MIN_BLUR_SCORE: float = 8.0

    @classmethod
    def analyze_image(cls, image_path: str, species: Optional[str] = "Cattle") -> ImageQualityReport:
        """
        Performs comprehensive quality and domain checks on a given image file.
        """
        path = Path(image_path)
        if not path.is_file():
            return ImageQualityReport(
                is_sufficient=False,
                quality_score=0.0,
                resolution=(0, 0),
                brightness=0.0,
                contrast=0.0,
                blur_score=0.0,
                issues=["FILE_NOT_FOUND"],
                status="INSUFFICIENT_IMAGE_QUALITY",
                message="Image file was not found on server storage."
            )

        try:
            with Image.open(path) as img:
                # 1. Check dimensions
                w, h = img.size
                gray = img.convert("L")
                gray_arr = np.array(gray, dtype=np.float32)

            # 2. Brightness (mean pixel intensity [0, 255])
            brightness = float(np.mean(gray_arr))

            # 3. Contrast (standard deviation of pixel intensity)
            contrast = float(np.std(gray_arr))

            # 4. Blur score (gradient energy variance)
            if gray_arr.shape[0] > 10 and gray_arr.shape[1] > 10:
                gy, gx = np.gradient(gray_arr)
                gnorm = np.sqrt(gx**2 + gy**2)
                blur_score = float(np.var(gnorm))
            else:
                blur_score = 0.0

            # 5. Evaluate degradation issues
            issues: List[str] = []
            if w < cls.MIN_WIDTH or h < cls.MIN_HEIGHT:
                issues.append("LOW_RESOLUTION")
            if brightness < cls.MIN_BRIGHTNESS:
                issues.append("POOR_LIGHTING_DARK")
            elif brightness > cls.MAX_BRIGHTNESS:
                issues.append("OVEREXPOSURE_FLASH")
            if contrast < cls.MIN_CONTRAST:
                issues.append("LOW_CONTRAST")
            if blur_score < cls.MIN_BLUR_SCORE:
                issues.append("MOTION_BLUR_DEFOCUS")

            # 6. Check Species Scope
            is_bovine_valid = model_scope_registry.is_species_validated(species)
            if not is_bovine_valid:
                issues.append("UNSUPPORTED_SPECIES")

            # 7. Compute aggregate quality score (0 - 100)
            score = 100.0
            if "LOW_RESOLUTION" in issues:
                score -= 30.0
            if "POOR_LIGHTING_DARK" in issues or "OVEREXPOSURE_FLASH" in issues:
                score -= 25.0
            if "LOW_CONTRAST" in issues:
                score -= 15.0
            if "MOTION_BLUR_DEFOCUS" in issues:
                score -= 25.0
            if "UNSUPPORTED_SPECIES" in issues:
                score -= 20.0
            score = max(5.0, min(100.0, score))

            # 8. Determine final status
            if "UNSUPPORTED_SPECIES" in issues:
                status = "MODEL_NOT_VALIDATED_FOR_SPECIES"
                message = f"AI vision model is validated exclusively for Cattle (Bovine). Species '{species}' requires direct veterinary examination."
                is_sufficient = False
            elif len(issues) > 0 and ("LOW_RESOLUTION" in issues or "MOTION_BLUR_DEFOCUS" in issues or "POOR_LIGHTING_DARK" in issues):
                status = "INSUFFICIENT_IMAGE_QUALITY"
                issue_str = ", ".join(issues)
                message = f"Image quality is insufficient for reliable visual screening ({issue_str}). Clear daylight photograph recommended."
                is_sufficient = False
            elif score < 60.0:
                status = "POTENTIAL_OUT_OF_DOMAIN"
                message = "Visual characteristics differ from validated clinical baseline. Results flagged for veterinary review."
                is_sufficient = True  # Can screen with caveat
            else:
                status = "QUALITY_VERIFIED"
                message = "Image clarity and exposure meet clinical diagnostic triage standards."
                is_sufficient = True

            return ImageQualityReport(
                is_sufficient=is_sufficient,
                quality_score=score,
                resolution=(w, h),
                brightness=brightness,
                contrast=contrast,
                blur_score=blur_score,
                issues=issues,
                status=status,
                message=message
            )

        except Exception as e:
            return ImageQualityReport(
                is_sufficient=False,
                quality_score=0.0,
                resolution=(0, 0),
                brightness=0.0,
                contrast=0.0,
                blur_score=0.0,
                issues=["CORRUPTED_IMAGE"],
                status="INSUFFICIENT_IMAGE_QUALITY",
                message=f"Failed to decode image data: {e}"
            )


image_quality_analyzer = ImageQualityAnalyzer()
