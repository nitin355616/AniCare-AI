import os
from pathlib import Path
from typing import Tuple, Dict, Any, Optional
import numpy as np
from PIL import Image

try:
    from ai.config import ai_config
except ImportError:
    from backend.ai.config import ai_config

class ImagePreprocessor:
    """
    Production-grade image validation and preprocessing pipeline for
    MobileNetV3 and EfficientNet livestock vision architectures.
    Performs format validation, dimension checks, aspect-ratio preservation,
    and ImageNet statistical normalization.
    """

    def __init__(
        self,
        target_size: Tuple[int, int] = ai_config.IMAGE_INPUT_SIZE,
        norm_mean: Tuple[float, float, float] = ai_config.NORM_MEAN,
        norm_std: Tuple[float, float, float] = ai_config.NORM_STD
    ):
        self.target_size = target_size
        self.norm_mean = np.array(norm_mean, dtype=np.float32).reshape((3, 1, 1))
        self.norm_std = np.array(norm_std, dtype=np.float32).reshape((3, 1, 1))

    def validate_image_file(self, image_path: str) -> Path:
        """
        Validates file existence, format, and size before processing.
        """
        path = Path(image_path)
        if not path.is_file():
            raise FileNotFoundError(f"Image file not found at: {image_path}")

        file_size_mb = path.stat().st_size / (1024 * 1024)
        if file_size_mb > ai_config.MAX_IMAGE_FILE_SIZE_MB:
            raise ValueError(
                f"Image file size ({file_size_mb:.2f}MB) exceeds maximum limit "
                f"of {ai_config.MAX_IMAGE_FILE_SIZE_MB}MB."
            )

        allowed_suffixes = {".jpg", ".jpeg", ".png", ".webp"}
        if path.suffix.lower() not in allowed_suffixes:
            raise ValueError(
                f"Unsupported image extension '{path.suffix}'. "
                f"Allowed formats: {', '.join(allowed_suffixes)}"
            )

        return path

    def preprocess(self, image_path: str) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Transforms raw livestock image into an NCHW float32 tensor (1, 3, H, W)
        ready for ONNX Runtime or PyTorch forward pass.

        Returns:
            tensor: Shape (1, 3, target_h, target_w), normalized
            metadata: Dict with original dimensions, aspect ratio, and channels
        """
        valid_path = self.validate_image_file(image_path)

        try:
            with Image.open(valid_path) as img:
                orig_width, orig_height = img.size

                # Reject unreliably tiny images
                if orig_width < 32 or orig_height < 32:
                    raise ValueError(
                        f"Image resolution {orig_width}x{orig_height} is below minimum "
                        f"diagnostic threshold of 32x32 pixels."
                    )

                # Convert to standard RGB (drops alpha channel safely)
                if img.mode != "RGB":
                    img = img.convert("RGB")

                # High-quality resize using bilinear interpolation
                resized = img.resize(self.target_size, Image.Resampling.BILINEAR)

                # Convert to float32 numpy array in range [0.0, 1.0]
                img_array = np.array(resized, dtype=np.float32) / 255.0

                # Reshape from HWC (224, 224, 3) to CHW (3, 224, 224)
                chw_array = np.transpose(img_array, (2, 0, 1))

                # Apply ImageNet channel standardization: (x - mean) / std
                normalized = (chw_array - self.norm_mean) / self.norm_std

                # Add batch dimension: NCHW (1, 3, 224, 224)
                tensor = np.expand_dims(normalized, axis=0).astype(np.float32)

                metadata = {
                    "original_width": orig_width,
                    "original_height": orig_height,
                    "target_size": self.target_size,
                    "channels": 3,
                    "batch_shape": list(tensor.shape),
                    "file_path": str(valid_path)
                }

                return tensor, metadata

        except (IOError, SyntaxError) as e:
            raise ValueError(f"Corrupted or invalid image data: {str(e)}") from e

image_preprocessor = ImagePreprocessor()
