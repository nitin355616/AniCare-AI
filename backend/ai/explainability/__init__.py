"""
AniCare AI — Explainability & Saliency Heatmap Subsystem
Provides visual attention saliency (Grad-CAM) to visualize
regions contributing to convolutional model representations.
"""

from .gradcam import gradcam_explainer, GradCAMExplainer

__all__ = ["gradcam_explainer", "GradCAMExplainer"]
