"""
AniCare AI — Multi-Crop & Tiled Image Preprocessor
Performs overlapping spatial patch extraction and multi-scale visual scanning
to detect localized cutaneous nodules in distant whole-animal photography.
"""

import os
from pathlib import Path
from typing import Tuple, List, Dict, Any, Optional
import numpy as np
from PIL import Image

try:
    from ai.config import ai_config
    from ai.preprocessing.image_preprocessor import image_preprocessor
except ImportError:
    from backend.ai.config import ai_config
    from backend.ai.preprocessing.image_preprocessor import image_preprocessor


class TiledPreprocessor:
    """
    Multi-crop spatial decomposition engine.
    Extracts global overview + high-resolution overlapping localized patches
    to counteract resolution attenuation on distant animal photographs.
    """

    def __init__(
        self,
        target_size: Tuple[int, int] = ai_config.IMAGE_INPUT_SIZE,
        crop_overlap_ratio: float = 0.20,
        center_crop_scale: float = 0.80
    ):
        self.target_size = target_size
        self.crop_overlap_ratio = crop_overlap_ratio
        self.center_crop_scale = center_crop_scale
        self.norm_mean = np.array(ai_config.NORM_MEAN, dtype=np.float32).reshape((3, 1, 1))
        self.norm_std = np.array(ai_config.NORM_STD, dtype=np.float32).reshape((3, 1, 1))

    def _normalize_pil(self, pil_img: Image.Image) -> np.ndarray:
        """Converts PIL crop to ImageNet-normalized NCHW float32 tensor."""
        resized = pil_img.resize(self.target_size, Image.Resampling.BILINEAR)
        arr = np.array(resized, dtype=np.float32) / 255.0
        chw = np.transpose(arr, (2, 0, 1))
        norm = (chw - self.norm_mean) / self.norm_std
        return np.expand_dims(norm, axis=0).astype(np.float32)

    def extract_crops(self, image_path: str) -> Tuple[List[np.ndarray], Dict[str, Any]]:
        """
        Extracts 5 multi-scale crops:
        1. Full global image (resized)
        2. Center crop (zoom 1.25x)
        3. Top-Left quadrant
        4. Top-Right quadrant
        5. Bottom-Left quadrant
        6. Bottom-Right quadrant
        """
        valid_path = image_preprocessor.validate_image_file(image_path)
        with Image.open(valid_path) as img:
            rgb_img = img.convert("RGB")
            w, h = rgb_img.size

            crops: List[np.ndarray] = []
            crop_metadata: List[Dict[str, Any]] = []

            # 1. Global Crop (standard baseline view)
            global_tensor = self._normalize_pil(rgb_img)
            crops.append(global_tensor)
            crop_metadata.append({"type": "global", "box": [0, 0, w, h]})

            # 2. Center Crop
            cw = int(w * self.center_crop_scale)
            ch = int(h * self.center_crop_scale)
            cx0 = (w - cw) // 2
            cy0 = (h - ch) // 2
            center_crop = rgb_img.crop((cx0, cy0, cx0 + cw, cy0 + ch))
            crops.append(self._normalize_pil(center_crop))
            crop_metadata.append({"type": "center_zoom", "box": [cx0, cy0, cx0 + cw, cy0 + ch]})

            # 3-6. Four Overlapping Quadrants (Half-width/height + overlap)
            qw = int(w * 0.60)
            qh = int(h * 0.60)

            quadrants = [
                ("top_left", 0, 0, qw, qh),
                ("top_right", w - qw, 0, w, qh),
                ("bottom_left", 0, h - qh, qw, h),
                ("bottom_right", w - qw, h - qh, w, h)
            ]

            for name, x0, y0, x1, y1 in quadrants:
                quad_crop = rgb_img.crop((x0, y0, x1, y1))
                crops.append(self._normalize_pil(quad_crop))
                crop_metadata.append({"type": f"quadrant_{name}", "box": [x0, y0, x1, y1]})

        meta = {
            "image_path": str(valid_path),
            "original_dimensions": [w, h],
            "crop_count": len(crops),
            "crops": crop_metadata
        }
        return crops, meta

    @staticmethod
    def aggregate_crop_predictions(
        crop_lsd_probabilities: List[float],
        method: str = "conservative_ensemble"
    ) -> Dict[str, Any]:
        """
        Aggregates multi-crop probabilities.
        - global_prob: Probability from the global uncropped view (crop 0).
        - max_patch_prob: Peak localized lesion probability found across sub-crops.
        - conservative_ensemble: 0.6 * global + 0.4 * max_patch.
          Ensures that an acute localized lesion cluster raises vigilance,
          while mitigating spurious single-patch false alarms.
        """
        if not crop_lsd_probabilities:
            return {"final_prob": 0.0, "global_prob": 0.0, "max_patch_prob": 0.0}

        global_prob = crop_lsd_probabilities[0]
        patch_probs = crop_lsd_probabilities[1:] if len(crop_lsd_probabilities) > 1 else [global_prob]
        max_patch_prob = max(patch_probs)
        mean_patch_prob = sum(patch_probs) / len(patch_probs)

        if method == "conservative_ensemble":
            # Blended weighting: retains global context while surfacing localized hotspots
            final_prob = (0.60 * global_prob) + (0.40 * max_patch_prob)
        elif method == "max_pooling":
            final_prob = max_patch_prob
        else:
            final_prob = global_prob

        return {
            "final_prob": round(float(final_prob), 4),
            "global_prob": round(float(global_prob), 4),
            "max_patch_prob": round(float(max_patch_prob), 4),
            "mean_patch_prob": round(float(mean_patch_prob), 4),
            "all_crop_probs": [round(float(p), 4) for p in crop_lsd_probabilities]
        }


tiled_preprocessor = TiledPreprocessor()
