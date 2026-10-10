"""
AniCare AI — Loss Functions for Imbalanced Veterinary Vision Classification
Implements Weighted Cross-Entropy and Focal Loss with dynamic alpha weighting.
"""

from typing import Optional, List
import torch
import torch.nn as nn
import torch.nn.functional as F


class FocalLoss(nn.Module):
    """
    Multi-class Focal Loss (Lin et al., ICCV 2017).
    Focuses learning on hard minority examples (Lumpy Skin Disease)
    while down-weighting easy background/normal skin examples.
    FL(p_t) = -alpha_t * (1 - p_t)^gamma * log(p_t)
    """

    def __init__(
        self,
        alpha: Optional[torch.Tensor] = None,
        gamma: float = 2.0,
        reduction: str = "mean"
    ):
        super().__init__()
        self.alpha = alpha
        self.gamma = gamma
        self.reduction = reduction

    def forward(self, inputs: torch.Tensor, targets: torch.Tensor) -> torch.Tensor:
        # Numerically stable computation using standard cross entropy loss
        ce_loss = F.cross_entropy(inputs, targets, reduction="none")
        pt = torch.exp(-ce_loss)  # probability of true class

        if self.alpha is not None:
            if self.alpha.device != inputs.device:
                self.alpha = self.alpha.to(inputs.device)
            at = self.alpha.gather(0, targets)
            focal_loss = at * ((1.0 - pt) ** self.gamma) * ce_loss
        else:
            focal_loss = ((1.0 - pt) ** self.gamma) * ce_loss

        if self.reduction == "mean":
            return focal_loss.mean()
        elif self.reduction == "sum":
            return focal_loss.sum()
        else:
            return focal_loss


def create_criterion(
    loss_type: str,
    class_weights: List[float],
    focal_alpha: Optional[List[float]] = None,
    gamma: float = 2.0,
    device: str = "cpu"
) -> nn.Module:
    """Factory creating loss functions tailored to class imbalance settings."""
    if loss_type == "weighted_ce":
        w = torch.tensor(class_weights, dtype=torch.float32, device=device)
        return nn.CrossEntropyLoss(weight=w)
    elif loss_type == "focal":
        a = torch.tensor(focal_alpha or class_weights, dtype=torch.float32, device=device)
        return FocalLoss(alpha=a, gamma=gamma, reduction="mean")
    elif loss_type == "standard_ce":
        return nn.CrossEntropyLoss()
    else:
        raise ValueError(f"Unknown loss type: {loss_type}")
