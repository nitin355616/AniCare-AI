"""
AniCare AI — Grad-CAM Visual Explainability Engine
Generates Gradient-weighted Class Activation Mapping (Grad-CAM) heatmaps
for EfficientNet-B0 vision architectures to identify spatial regions
contributing to the convolutional model's visual representation.
"""

import os
import sys
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
import numpy as np
from PIL import Image

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BACKEND_DIR))

logger = logging.getLogger("anicare.explainability")


class GradCAMExplainer:
    """
    Grad-CAM engine hooked into the penultimate convolutional block of EfficientNet-B0.
    Operates as an asynchronous/on-demand explainability layer.
    """

    def __init__(self, checkpoint_path: Optional[Path] = None):
        self.checkpoint_path = checkpoint_path or (
            BACKEND_DIR / "ai" / "models" / "checkpoints" / "efficientnet_b0_focal_best.pt"
        )
        self.output_dir = BACKEND_DIR / "uploads" / "explanations"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._model = None
        self._target_layer = None
        self._gradients = None
        self._activations = None

    def is_available(self) -> bool:
        """Checks if PyTorch and physical checkpoint exist."""
        try:
            import torch  # noqa: F401
            return self.checkpoint_path.is_file()
        except ImportError:
            return False

    def _init_model(self):
        """Lazy instantiation of the PyTorch evaluation model for gradient tracing."""
        if self._model is not None:
            return self._model

        import torch
        from ai.training.model import BovineVisionClassifier

        if not self.checkpoint_path.is_file():
            raise FileNotFoundError(f"Checkpoint not found at: {self.checkpoint_path}")

        checkpoint = torch.load(self.checkpoint_path, map_location="cpu", weights_only=False)
        state_dict = checkpoint.get("state_dict", checkpoint.get("model_state_dict"))

        model = BovineVisionClassifier(architecture="efficientnet_b0", num_classes=2, pretrained=False)
        model.load_state_dict(state_dict)
        model.eval()

        # Target layer for EfficientNet-B0: last conv block in base features
        self._target_layer = model.base.features[-1]

        def save_activation(module, input, output):
            self._activations = output

        def save_gradient(module, grad_input, grad_output):
            self._gradients = grad_output[0]

        self._target_layer.register_forward_hook(save_activation)
        self._target_layer.register_full_backward_hook(save_gradient)

        self._model = model
        return self._model

    def generate_heatmap(
        self,
        image_path: str,
        target_class_idx: int = 1,
        image_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes forward + backward pass, computes Grad-CAM saliency,
        and saves an alpha-blended heatmap overlay.
        """
        if not self.is_available():
            return {
                "status": "UNAVAILABLE",
                "message": "Grad-CAM engine unavailable: PyTorch checkpoint pending or runtime absent.",
                "heatmap_url": None,
                "interpretation": "Visual explainability pending",
                "scientific_disclaimer": "Visual attribution requires loaded convolutional gradient hooks."
            }

        try:
            import torch
            from ai.training.transforms import get_eval_transforms

            model = self._init_model()
            img_path = Path(image_path)
            if not img_path.is_file():
                return {"status": "ERROR", "message": f"Image file not found: {image_path}"}

            with Image.open(img_path) as orig_img:
                rgb_orig = orig_img.convert("RGB")
                orig_w, orig_h = rgb_orig.size

            transform = get_eval_transforms(image_size=224)
            input_tensor = transform(rgb_orig).unsqueeze(0)  # Shape (1, 3, 224, 224)

            model.zero_grad()
            logits = model(input_tensor)
            score = logits[0, target_class_idx]
            score.backward()

            # Global average pooling of gradients: weights alpha_k
            gradients = self._gradients[0].detach().numpy()  # Shape (C, H, W)
            activations = self._activations[0].detach().numpy()  # Shape (C, H, W)

            weights = np.mean(gradients, axis=(1, 2))  # Shape (C,)

            cam = np.zeros(activations.shape[1:], dtype=np.float32)
            for i, w in enumerate(weights):
                cam += w * activations[i, :, :]

            cam = np.maximum(cam, 0)  # ReLU
            cam_max = np.max(cam)
            if cam_max > 0:
                cam = cam / cam_max

            # Peak activation coordinates (normalized 0.0 - 1.0)
            peak_y, peak_x = np.unravel_index(np.argmax(cam), cam.shape)
            peak_norm_coords = [round(float(peak_x / cam.shape[1]), 3), round(float(peak_y / cam.shape[0]), 3)]

            # Resize CAM to match original image dimensions
            cam_pil = Image.fromarray((cam * 255).astype(np.uint8)).resize((orig_w, orig_h), Image.Resampling.BILINEAR)
            cam_resized = np.array(cam_pil, dtype=np.float32) / 255.0

            # Generate Heatmap Color Overlay (Jet color map approximation)
            overlay_arr = np.array(rgb_orig, dtype=np.float32) / 255.0

            # Jet colormap formula in pure numpy
            heatmap_r = np.clip(1.5 - np.abs(4.0 * cam_resized - 3.0), 0.0, 1.0)
            heatmap_g = np.clip(1.5 - np.abs(4.0 * cam_resized - 2.0), 0.0, 1.0)
            heatmap_b = np.clip(1.5 - np.abs(4.0 * cam_resized - 1.0), 0.0, 1.0)
            heatmap_rgb = np.stack([heatmap_r, heatmap_g, heatmap_b], axis=-1)

            # Alpha blend 50% heatmap, 50% original image
            blended = (0.50 * overlay_arr) + (0.50 * heatmap_rgb)
            blended_uint8 = (np.clip(blended, 0.0, 1.0) * 255).astype(np.uint8)

            img_slug = image_id or img_path.stem
            out_filename = f"{img_slug}_gradcam.jpg"
            out_path = self.output_dir / out_filename
            Image.fromarray(blended_uint8).save(out_path, format="JPEG", quality=90)

            return {
                "status": "SUCCESS",
                "explanation_type": "GRAD_CAM",
                "target_class": "Lumpy Skin Disease" if target_class_idx == 1 else "Healthy / Normal",
                "target_class_idx": target_class_idx,
                "heatmap_filename": out_filename,
                "heatmap_url": f"/uploads/explanations/{out_filename}",
                "heatmap_saved_path": str(out_path),
                "peak_activation_coords": peak_norm_coords,
                "interpretation": "Areas contributing to the model's visual assessment",
                "scientific_disclaimer": (
                    "Grad-CAM visualizes receptive-field feature gradient attribution in convolutional layers. "
                    "It indicates spatial regions influencing the classifier and does NOT assert that biological "
                    "infection is definitively isolated to the highlighted region."
                )
            }

        except Exception as exc:
            logger.error(f"Grad-CAM generation error: {exc}", exc_info=True)
            return {
                "status": "ERROR",
                "message": f"Grad-CAM processing exception: {str(exc)}",
                "heatmap_url": None,
                "interpretation": "Visual explainability encountered processing error",
                "scientific_disclaimer": "Diagnostic review must rely on certified veterinary clinical inspection."
            }


gradcam_explainer = GradCAMExplainer()
