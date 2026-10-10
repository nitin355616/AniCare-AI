# AniCare AI — Visual Explainability (Grad-CAM)

## Overview

The `ai/explainability` module provides Gradient-weighted Class Activation Mapping (Grad-CAM) for deep convolutional vision models in AniCare AI.

Grad-CAM generates coarse 2D heatmaps highlighting discriminative spatial regions in an input photograph that contributed positively to the convolutional network's class prediction.

---

## Architectural Details

```
Input Image (224x224 RGB)
       │
       ▼
EfficientNet-B0 Backbone (base.features)
       │
       ▼
Target Penultimate Conv Layer (base.features[-1] -> Conv2dNormActivation / 1280-d)
  ├── Forward Hook: Captures feature activations A_k
  └── Backward Hook: Captures incoming gradients dY/dA_k for target class
       │
       ▼
Global Average Pooling of Gradients:
  α_k = (1/Z) * Σ Σ (dY / dA_k_ij)
       │
       ▼
Linear Combination & Rectification:
  L_GradCAM = ReLU( Σ α_k * A_k )
       │
       ▼
Bilinear Upsampling to Original Resolution (WxH)
       │
       ▼
COLORMAP_JET Alpha Overlay Blending (alpha=0.45)
       │
       ▼
Exported PNG -> backend/uploads/explanations/gradcam_{image_id}_{hash}.png
```

---

## Clinical Safety & Veterinary Guidance

1. **Non-Diagnostic Nature**: Grad-CAM saliency heatmaps indicate *visual correlation*, not confirmed histological or microbiological etiologies.
2. **Pathological Framing**: Saliency peaks over nodular skin lesions assist veterinary officers in confirming whether the AI attended to true cutaneous pathology rather than background artifacts (e.g. soil texture, halters, or pen slats).
3. **Graceful Fallback**: If the deep PyTorch runtime or checkpoint weights are not mounted, the module returns an informative `UNAVAILABLE` payload without crashing the inference pipeline or degrading real-time triage.

---

## Usage

```python
from ai.explainability import gradcam_explainer

result = gradcam_explainer.generate_heatmap(
    image_path="backend/uploads/sample.jpg",
    target_class_idx=1,  # 1 = Lumpy Skin Disease, 0 = Healthy
    image_id="IMG-TEST01"
)

# Output structure:
# {
#   "status": "SUCCESS",
#   "heatmap_url": "/uploads/explanations/gradcam_IMG-TEST01_...png",
#   "interpretation": "Discriminative saliency concentrated in 1 discrete anatomical zone(s)...",
#   "scientific_disclaimer": "Grad-CAM highlights convolutional activation regions..."
# }
```
