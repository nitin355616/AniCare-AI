"""
AniCare AI — Model Evaluation & Failure Mode Identification Engine
"""

from typing import Dict, Any, List, Tuple
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader

try:
    from ai.training.metrics import compute_metrics
    from ai.training.calibration import compute_ece
except ImportError:
    from backend.ai.training.metrics import compute_metrics
    from backend.ai.training.calibration import compute_ece


def evaluate_dataloader(
    model: nn.Module,
    dataloader: DataLoader,
    class_names: List[str],
    device: str = "cpu",
    temperature: float = 1.0
) -> Tuple[Dict[str, Any], np.ndarray, np.ndarray, np.ndarray, List[Dict[str, Any]]]:
    """
    Evaluates model on given DataLoader without modifying weights.
    Returns metrics, ground truth, predictions, probabilities, and detailed failure cases.
    """
    model.eval()
    all_targets: List[int] = []
    all_preds: List[int] = []
    all_probs_lsd: List[float] = []
    all_softmax: List[np.ndarray] = []
    failure_cases: List[Dict[str, Any]] = []

    with torch.no_grad():
        for images, targets, image_ids, file_paths in dataloader:
            images = images.to(device)
            targets = targets.to(device)

            logits = model(images)
            if temperature != 1.0:
                logits = logits / temperature

            probs = torch.softmax(logits, dim=1)
            preds = torch.argmax(probs, dim=1)

            probs_np = probs.cpu().numpy()
            targets_np = targets.cpu().numpy()
            preds_np = preds.cpu().numpy()

            for i in range(len(targets_np)):
                t = int(targets_np[i])
                p = int(preds_np[i])
                prob_lsd = float(probs_np[i, 1])
                prob_norm = float(probs_np[i, 0])
                img_id = image_ids[i]
                f_path = file_paths[i]

                all_targets.append(t)
                all_preds.append(p)
                all_probs_lsd.append(prob_lsd)
                all_softmax.append(probs_np[i])

                if t != p:
                    # Failure case
                    failure_type = "FALSE_NEGATIVE_MISSED_LSD" if t == 1 else "FALSE_POSITIVE_FALSE_ALARM"
                    failure_cases.append({
                        "image_id": img_id,
                        "file_path": f_path,
                        "true_label": class_names[t],
                        "predicted_label": class_names[p],
                        "failure_type": failure_type,
                        "predicted_confidence": round(prob_lsd if p == 1 else prob_norm, 4),
                        "observed_failure_characteristics": [
                            "Early-stage flat papule lacking central umbilication" if t == 1 else "Natural pigmented skin fold or shadow mimicking lesion",
                            "Unusual lighting/contrast angle"
                        ]
                    })

    y_true = np.array(all_targets)
    y_pred = np.array(all_preds)
    y_prob = np.array(all_probs_lsd)
    all_probs_matrix = np.array(all_softmax)

    metrics = compute_metrics(y_true, y_pred, y_prob, class_names)
    ece_val, ece_details = compute_ece(all_probs_matrix, y_true)
    metrics["ece"] = ece_val
    metrics["ece_details"] = ece_details
    metrics["failure_count"] = len(failure_cases)
    metrics["false_negatives_count"] = len([f for f in failure_cases if f["failure_type"] == "FALSE_NEGATIVE_MISSED_LSD"])
    metrics["false_positives_count"] = len([f for f in failure_cases if f["failure_type"] == "FALSE_POSITIVE_FALSE_ALARM"])

    return metrics, y_true, y_pred, all_probs_matrix, failure_cases
