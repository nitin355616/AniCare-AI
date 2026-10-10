"""
AniCare AI — Confidence Calibration & Temperature Scaling
Implements Expected Calibration Error (ECE) calculation and post-hoc Temperature Scaling.
"""

from typing import Tuple, Dict, Any
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim


def compute_ece(
    probs: np.ndarray,
    labels: np.ndarray,
    n_bins: int = 10
) -> Tuple[float, Dict[str, Any]]:
    """
    Computes Expected Calibration Error (ECE) (Guo et al., ICML 2017).
    Partitions predictions into confidence bins and computes weighted absolute calibration gap.
    """
    # For binary classification, maximum confidence and predicted class
    confidences = np.max(probs, axis=1)
    predictions = np.argmax(probs, axis=1)
    accuracies = (predictions == labels).astype(float)

    bin_boundaries = np.linspace(0, 1, n_bins + 1)
    bin_lowers = bin_boundaries[:-1]
    bin_uppers = bin_boundaries[1:]

    ece = 0.0
    bin_details = []

    for bin_lower, bin_upper in zip(bin_lowers, bin_uppers):
        in_bin = (confidences > bin_lower) & (confidences <= bin_upper)
        prop_in_bin = np.mean(in_bin)

        if prop_in_bin > 0:
            accuracy_in_bin = np.mean(accuracies[in_bin])
            avg_confidence_in_bin = np.mean(confidences[in_bin])
            abs_gap = np.abs(avg_confidence_in_bin - accuracy_in_bin)
            ece += abs_gap * prop_in_bin
            bin_details.append({
                "bin": f"[{bin_lower:.2f}, {bin_upper:.2f}]",
                "sample_count": int(np.sum(in_bin)),
                "accuracy": round(float(accuracy_in_bin), 4),
                "confidence": round(float(avg_confidence_in_bin), 4),
                "gap": round(float(abs_gap), 4)
            })

    return round(float(ece), 4), {"ece": round(float(ece), 4), "bins": bin_details}


class ModelTemperatureScaler(nn.Module):
    """
    Calibrates logits by optimizing a single learned temperature parameter T > 0 on validation set.
    logits_calibrated = logits / T
    """

    def __init__(self):
        super().__init__()
        self.temperature = nn.Parameter(torch.ones(1) * 1.5)

    def forward(self, logits: torch.Tensor) -> torch.Tensor:
        temp = self.temperature.clamp(min=0.01)
        return logits / temp

    def fit(self, val_logits: torch.Tensor, val_labels: torch.Tensor, max_iter: int = 50) -> float:
        """Optimizes temperature to minimize NLL on validation set."""
        criterion = nn.CrossEntropyLoss()
        optimizer = optim.LBFGS([self.temperature], lr=0.01, max_iter=max_iter)

        def eval_step():
            optimizer.zero_grad()
            loss = criterion(self.forward(val_logits), val_labels)
            loss.backward()
            return loss

        optimizer.step(eval_step)
        optimal_t = float(self.temperature.item())
        return round(optimal_t, 4)
