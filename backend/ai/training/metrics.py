"""
AniCare AI — Quantitative Metrics Calculation Engine
Computes clinical sensitivity, specificity, Macro F1, ROC-AUC, and confusion matrices.
"""

from typing import Dict, Any, List, Tuple
import numpy as np
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    roc_auc_score,
    precision_recall_curve,
    auc,
    classification_report,
)


def compute_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_prob: np.ndarray,
    class_names: List[str]
) -> Dict[str, Any]:
    """
    Computes rigorous clinical evaluation metrics.

    Args:
        y_true: Ground truth binary labels (0 or 1).
        y_pred: Predicted class indices (0 or 1).
        y_prob: Predicted softmax probability for class 1 (LSD).
        class_names: List of class strings, e.g. ["Healthy / Normal", "Lumpy Skin Disease"].

    Returns:
        Structured metrics dictionary.
    """
    acc = float(accuracy_score(y_true, y_pred))
    macro_f1 = float(f1_score(y_true, y_pred, average="macro", zero_division=0))
    macro_prec = float(precision_score(y_true, y_pred, average="macro", zero_division=0))
    macro_rec = float(recall_score(y_true, y_pred, average="macro", zero_division=0))

    # Binary metrics specifically for Class 1 (Lumpy Skin Disease)
    lsd_prec = float(precision_score(y_true, y_pred, pos_label=1, zero_division=0))
    lsd_rec = float(recall_score(y_true, y_pred, pos_label=1, zero_division=0))
    lsd_f1 = float(f1_score(y_true, y_pred, pos_label=1, zero_division=0))

    # Binary metrics for Class 0 (Healthy / Normal)
    norm_prec = float(precision_score(y_true, y_pred, pos_label=0, zero_division=0))
    norm_rec = float(recall_score(y_true, y_pred, pos_label=0, zero_division=0))  # Specificity for LSD
    norm_f1 = float(f1_score(y_true, y_pred, pos_label=0, zero_division=0))

    # Confusion matrix: rows = true, cols = pred
    cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
    # [[TN, FP],
    #  [FN, TP]]
    tn, fp, fn, tp = int(cm[0, 0]), int(cm[0, 1]), int(cm[1, 0]), int(cm[1, 1])

    # Specificity = TN / (TN + FP)
    specificity = float(tn / (tn + fp)) if (tn + fp) > 0 else 0.0

    # ROC-AUC
    try:
        roc_auc = float(roc_auc_score(y_true, y_prob))
    except Exception:
        roc_auc = 0.0

    # PR-AUC for minority class (LSD)
    try:
        precisions, recalls, _ = precision_recall_curve(y_true, y_prob, pos_label=1)
        pr_auc = float(auc(recalls, precisions))
    except Exception:
        pr_auc = 0.0

    report = {
        "accuracy": round(acc, 4),
        "macro_f1": round(macro_f1, 4),
        "macro_precision": round(macro_prec, 4),
        "macro_recall": round(macro_rec, 4),
        "lsd_sensitivity_recall": round(lsd_rec, 4),
        "lsd_precision": round(lsd_prec, 4),
        "lsd_f1": round(lsd_f1, 4),
        "healthy_specificity": round(specificity, 4),
        "healthy_precision": round(norm_prec, 4),
        "healthy_f1": round(norm_f1, 4),
        "roc_auc": round(roc_auc, 4),
        "pr_auc": round(pr_auc, 4),
        "confusion_matrix": {
            "true_negatives_healthy": tn,
            "false_positives_false_alarm": fp,
            "false_negatives_missed_lsd": fn,
            "true_positives_detected_lsd": tp,
            "raw_matrix": cm.tolist()
        },
        "per_class": {
            class_names[0]: {
                "precision": round(norm_prec, 4),
                "recall": round(norm_rec, 4),
                "f1": round(norm_f1, 4),
                "support": int(tn + fp)
            },
            class_names[1]: {
                "precision": round(lsd_prec, 4),
                "recall": round(lsd_rec, 4),
                "f1": round(lsd_f1, 4),
                "support": int(fn + tp)
            }
        }
    }
    return report
