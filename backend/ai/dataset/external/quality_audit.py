"""
AniCare AI — External Image Quality Auditor
Audits photometric metrics, dimensions, corruption, blur, and exposure.
Tiers into UNUSABLE, POOR, ACCEPTABLE, HIGH.
Logs rejection reasons without deleting rejected samples from the audit trail.
"""

import io
import hashlib
from enum import Enum
from typing import Dict, Any, List, Optional
from PIL import Image, ImageStat
import numpy as np


class QualityTier(str, Enum):
    UNUSABLE = "UNUSABLE"
    POOR = "POOR"
    ACCEPTABLE = "ACCEPTABLE"
    HIGH = "HIGH"


class ExternalQualityAuditor:
    """Evaluates image integrity and assigns quality tier."""

    MIN_WIDTH = 224
    MIN_HEIGHT = 224
    ALLOWED_FORMATS = ["JPEG", "PNG", "WEBP"]

    @classmethod
    def audit_image_bytes(
        cls,
        image_bytes: bytes,
        filename: str = "sample.jpg"
    ) -> Dict[str, Any]:
        """
        Runs comprehensive image audit.
        Returns detailed quality metrics and quality tier.
        """
        sha256 = hashlib.sha256(image_bytes).hexdigest()

        # Check readable file & corruption
        try:
            with Image.open(io.BytesIO(image_bytes)) as img:
                img_format = img.format
                width, height = img.size
                mode = img.mode

                if img_format not in cls.ALLOWED_FORMATS:
                    return {
                        "is_valid": False,
                        "quality_tier": QualityTier.UNUSABLE.value,
                        "rejection_reason": f"UNSUPPORTED_FORMAT: {img_format}",
                        "sha256": sha256,
                        "width": width,
                        "height": height
                    }

                if width < cls.MIN_WIDTH or height < cls.MIN_HEIGHT:
                    return {
                        "is_valid": False,
                        "quality_tier": QualityTier.UNUSABLE.value,
                        "rejection_reason": f"SUB_MINIMUM_RESOLUTION: {width}x{height} < {cls.MIN_WIDTH}x{cls.MIN_HEIGHT}",
                        "sha256": sha256,
                        "width": width,
                        "height": height
                    }

                # Ensure RGB mode conversion
                img_rgb = img.convert("RGB")
                img_gray = img.convert("L")
                arr = np.array(img_gray, dtype=np.float32)

                # Focus / blur (gradient variance)
                gy, gx = np.gradient(arr)
                gnorm = np.sqrt(gx**2 + gy**2)
                sharpness = float(np.var(gnorm))

                # Exposure / mean luminance
                mean_lum = float(np.mean(arr))
                is_underexposed = mean_lum < 35.0
                is_overexposed = mean_lum > 225.0
                is_blurry = sharpness < 25.0

                warnings: List[str] = []
                if is_blurry:
                    warnings.append(f"High optical/motion blur (sharpness {sharpness:.1f} < 25.0)")
                if is_underexposed:
                    warnings.append(f"Severe underexposure (mean luminance {mean_lum:.1f} < 35.0)")
                if is_overexposed:
                    warnings.append(f"Severe specular overexposure (mean luminance {mean_lum:.1f} > 225.0)")

                # Quality tiering
                if is_blurry and (is_underexposed or is_overexposed):
                    tier = QualityTier.POOR
                elif width >= 800 and height >= 800 and sharpness >= 50.0 and not is_underexposed and not is_overexposed:
                    tier = QualityTier.HIGH
                elif sharpness >= 30.0 and not is_underexposed and not is_overexposed:
                    tier = QualityTier.ACCEPTABLE
                else:
                    tier = QualityTier.POOR

                return {
                    "is_valid": True,
                    "quality_tier": tier.value,
                    "rejection_reason": None,
                    "sha256": sha256,
                    "width": width,
                    "height": height,
                    "format": img_format,
                    "sharpness": round(sharpness, 2),
                    "mean_luminance": round(mean_lum, 2),
                    "is_blurry": is_blurry,
                    "is_underexposed": is_underexposed,
                    "is_overexposed": is_overexposed,
                    "warnings": warnings
                }

        except Exception as e:
            return {
                "is_valid": False,
                "quality_tier": QualityTier.UNUSABLE.value,
                "rejection_reason": f"CORRUPT_OR_UNREADABLE_IMAGE: {str(e)}",
                "sha256": sha256,
                "width": 0,
                "height": 0
            }


quality_auditor = ExternalQualityAuditor()
