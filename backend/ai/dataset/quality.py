"""
AniCare AI — Dataset Image Quality & Integrity Checker
Provides corruption detection, resolution thresholds, exact hash matching (SHA-256, MD5),
and perceptual difference hashing (dHash) for near-duplicate identification.
"""

import os
import io
import hashlib
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field
from PIL import Image, UnidentifiedImageError

try:
    from ai.dataset.schema import ImageQualityEnum
except ImportError:
    from backend.ai.dataset.schema import ImageQualityEnum


SUPPORTED_IMAGE_FORMATS = {"JPEG", "JPG", "PNG", "WEBP", "BMP", "TIFF"}
MINIMUM_VIABLE_DIMENSION = 64
STANDARD_INPUT_DIMENSION = 224
HIGH_QUALITY_DIMENSION = 512
NEAR_DUPLICATE_HAMMING_THRESHOLD = 5


class ImageQualityAssessment(BaseModel):
    """Structured assessment result for a single dataset image."""
    is_valid: bool
    quality_tier: ImageQualityEnum
    file_format: Optional[str] = None
    width: int = 0
    height: int = 0
    aspect_ratio: float = 0.0
    md5_hash: Optional[str] = None
    sha256_hash: Optional[str] = None
    dhash: Optional[str] = None
    warnings: List[str] = Field(default_factory=list)
    error: Optional[str] = None


class ImageQualityChecker:
    """
    Validates image readability, format compliance, resolution sufficiency,
    exact cryptographic hashes, and perceptual similarity.
    """

    @staticmethod
    def compute_exact_hashes(image_bytes: bytes) -> Dict[str, str]:
        """Calculates MD5 and SHA-256 hexadecimal digests for exact duplicate detection."""
        return {
            "md5": hashlib.md5(image_bytes).hexdigest(),
            "sha256": hashlib.sha256(image_bytes).hexdigest()
        }

    @staticmethod
    def compute_dhash(image_input: Union[Image.Image, bytes, str], hash_size: int = 8) -> str:
        """
        Computes Difference Hash (dHash) for perceptual similarity and near-duplicate detection.
        Resizes to (hash_size + 1, hash_size), converts to grayscale, and compares adjacent pixels.
        Produces a 64-bit hexadecimal string for hash_size=8.
        """
        if isinstance(image_input, str):
            with open(image_input, "rb") as f:
                img = Image.open(f)
                img.load()
        elif isinstance(image_input, bytes):
            img = Image.open(io.BytesIO(image_input))
            img.load()
        elif isinstance(image_input, Image.Image):
            img = image_input
        else:
            raise ValueError("Unsupported image input type for dHash calculation.")

        # Grayscale and resize to (hash_size + 1, hash_size)
        gray = img.convert("L").resize((hash_size + 1, hash_size), Image.Resampling.LANCZOS)
        pixels = list(gray.getdata())

        difference = []
        for row in range(hash_size):
            for col in range(hash_size):
                left_pixel = pixels[row * (hash_size + 1) + col]
                right_pixel = pixels[row * (hash_size + 1) + col + 1]
                difference.append(left_pixel > right_pixel)

        # Convert boolean list to 64-bit integer, then 16-character hex
        decimal_val = 0
        for index, val in enumerate(difference):
            if val:
                decimal_val |= 1 << (len(difference) - 1 - index)

        hex_len = (hash_size * hash_size) // 4
        return f"{decimal_val:0{hex_len}x}"

    @staticmethod
    def hamming_distance(hash1: str, hash2: str) -> int:
        """Computes Hamming distance (bit difference) between two hexadecimal hash strings."""
        if len(hash1) != len(hash2):
            raise ValueError(f"Hash lengths do not match: {len(hash1)} vs {len(hash2)}")
        val1 = int(hash1, 16)
        val2 = int(hash2, 16)
        xor_result = val1 ^ val2
        return bin(xor_result).count("1")

    @classmethod
    def is_near_duplicate(cls, hash1: str, hash2: str, threshold: int = NEAR_DUPLICATE_HAMMING_THRESHOLD) -> bool:
        """Determines if two images are near-duplicates using dHash Hamming distance."""
        return cls.hamming_distance(hash1, hash2) <= threshold

    @classmethod
    def inspect_image_bytes(cls, image_bytes: bytes, file_name: str = "unknown") -> ImageQualityAssessment:
        """Thoroughly checks image bytes for corruption, resolution, format, and hashes."""
        warnings: List[str] = []
        hashes = cls.compute_exact_hashes(image_bytes)

        try:
            with Image.open(io.BytesIO(image_bytes)) as img:
                img.verify()
        except (UnidentifiedImageError, OSError, SyntaxError) as e:
            return ImageQualityAssessment(
                is_valid=False,
                quality_tier=ImageQualityEnum.UNUSABLE,
                md5_hash=hashes["md5"],
                sha256_hash=hashes["sha256"],
                error=f"Corrupt or unreadable image file ({file_name}): {str(e)}",
                warnings=["File bytes cannot be decoded as a valid image."]
            )

        # Reopen to read dimensions and actual metadata after verify() invalidated stream
        try:
            with Image.open(io.BytesIO(image_bytes)) as img:
                img.load()
                fmt = (img.format or "UNKNOWN").upper()
                width, height = img.size
                dhash_val = cls.compute_dhash(img)
        except Exception as e:
            return ImageQualityAssessment(
                is_valid=False,
                quality_tier=ImageQualityEnum.UNUSABLE,
                md5_hash=hashes["md5"],
                sha256_hash=hashes["sha256"],
                error=f"Failed loading decompressed pixel buffer ({file_name}): {str(e)}",
                warnings=["Image header was valid, but decompressed pixel stream failed."]
            )

        if fmt not in SUPPORTED_IMAGE_FORMATS:
            warnings.append(f"Format '{fmt}' is outside standard formats ({', '.join(sorted(SUPPORTED_IMAGE_FORMATS))}).")

        aspect_ratio = round(width / max(height, 1), 3)
        if aspect_ratio > 3.0 or aspect_ratio < 0.33:
            warnings.append(f"Extreme aspect ratio ({aspect_ratio}:1) may cause severe distortion during square resizing.")

        # Resolution tier categorization
        if width < MINIMUM_VIABLE_DIMENSION or height < MINIMUM_VIABLE_DIMENSION:
            warnings.append(f"Resolution {width}x{height} is below minimum viable threshold ({MINIMUM_VIABLE_DIMENSION}x{MINIMUM_VIABLE_DIMENSION}).")
            quality_tier = ImageQualityEnum.UNUSABLE
            is_valid = False
        elif width < STANDARD_INPUT_DIMENSION or height < STANDARD_INPUT_DIMENSION:
            warnings.append(f"Resolution {width}x{height} is below standard CNN input dimension ({STANDARD_INPUT_DIMENSION}x{STANDARD_INPUT_DIMENSION}). Upsampling required.")
            quality_tier = ImageQualityEnum.POOR
            is_valid = True
        elif width >= HIGH_QUALITY_DIMENSION and height >= HIGH_QUALITY_DIMENSION:
            quality_tier = ImageQualityEnum.HIGH
            is_valid = True
        else:
            quality_tier = ImageQualityEnum.ACCEPTABLE
            is_valid = True

        return ImageQualityAssessment(
            is_valid=is_valid,
            quality_tier=quality_tier,
            file_format=fmt,
            width=width,
            height=height,
            aspect_ratio=aspect_ratio,
            md5_hash=hashes["md5"],
            sha256_hash=hashes["sha256"],
            dhash=dhash_val,
            warnings=warnings,
            error=None
        )

    @classmethod
    def inspect_file(cls, file_path: str) -> ImageQualityAssessment:
        """Inspects an image from local filesystem path."""
        if not os.path.exists(file_path):
            return ImageQualityAssessment(
                is_valid=False,
                quality_tier=ImageQualityEnum.UNUSABLE,
                error=f"File not found on filesystem: {file_path}",
                warnings=["File does not exist."]
            )
        try:
            with open(file_path, "rb") as f:
                content = f.read()
            return cls.inspect_image_bytes(content, file_name=os.path.basename(file_path))
        except Exception as e:
            return ImageQualityAssessment(
                is_valid=False,
                quality_tier=ImageQualityEnum.UNUSABLE,
                error=f"Filesystem read error for {file_path}: {str(e)}",
                warnings=["Could not read file from storage."]
            )
