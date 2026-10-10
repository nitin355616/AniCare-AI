"""
AniCare AI — Vision Model Factory & Fine-Tuning Controller
Implements MobileNetV3-Large and EfficientNet-B0 backbones with two-phase parameter freezing.
"""

from typing import Tuple, Dict, Any
import torch
import torch.nn as nn
import torchvision.models as models


class BovineVisionClassifier(nn.Module):
    """
    Wrapper around deep CNN backbones providing explicit control
    over two-phase transfer learning and layer freezing.
    """

    def __init__(self, architecture: str, num_classes: int = 2, pretrained: bool = True):
        super().__init__()
        self.architecture = architecture
        self.num_classes = num_classes
        self.pretrained = pretrained

        if architecture == "mobilenet_v3_large":
            weights = models.MobileNet_V3_Large_Weights.DEFAULT if pretrained else None
            self.base = models.mobilenet_v3_large(weights=weights)
            in_features = self.base.classifier[3].in_features
            # Replace final classification projection
            self.base.classifier[3] = nn.Linear(in_features, num_classes)
            self.weight_provenance = "PyTorch torchvision MobileNet_V3_Large_Weights.DEFAULT (BSD-3-Clause)"
        elif architecture == "efficientnet_b0":
            weights = models.EfficientNet_B0_Weights.DEFAULT if pretrained else None
            self.base = models.efficientnet_b0(weights=weights)
            in_features = self.base.classifier[1].in_features
            # Replace final classification projection
            self.base.classifier[1] = nn.Linear(in_features, num_classes)
            self.weight_provenance = "PyTorch torchvision EfficientNet_B0_Weights.DEFAULT (BSD-3-Clause)"
        else:
            raise ValueError(f"Unsupported model architecture: {architecture}")

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.base(x)

    def freeze_backbone(self) -> None:
        """Phase 1: Freezes all feature extraction layers, leaving only classifier trainable."""
        if self.architecture == "mobilenet_v3_large":
            for param in self.base.features.parameters():
                param.requires_grad = False
            for param in self.base.classifier.parameters():
                param.requires_grad = True
        elif self.architecture == "efficientnet_b0":
            for param in self.base.features.parameters():
                param.requires_grad = False
            for param in self.base.classifier.parameters():
                param.requires_grad = True

    def unfreeze_top_layers(self) -> None:
        """Phase 2: Unfreezes upper feature blocks for fine-tuning on veterinary features."""
        if self.architecture == "mobilenet_v3_large":
            # MobileNetV3 features has 17 inverted residual blocks.
            # Unfreeze the top 4 blocks (indices 13 to 16)
            for idx, child in enumerate(self.base.features):
                if idx >= 13:
                    for param in child.parameters():
                        param.requires_grad = True
        elif self.architecture == "efficientnet_b0":
            # EfficientNet features has 9 stage blocks.
            # Unfreeze top stages (indices 6, 7, 8)
            for idx, child in enumerate(self.base.features):
                if idx >= 6:
                    for param in child.parameters():
                        param.requires_grad = True

    def count_trainable_parameters(self) -> Tuple[int, int]:
        """Returns (trainable_params, total_params)."""
        trainable = sum(p.numel() for p in self.parameters() if p.requires_grad)
        total = sum(p.numel() for p in self.parameters())
        return trainable, total


def build_model(architecture: str, num_classes: int = 2, pretrained: bool = True) -> BovineVisionClassifier:
    """Builds and returns configured model wrapper."""
    return BovineVisionClassifier(architecture=architecture, num_classes=num_classes, pretrained=pretrained)
