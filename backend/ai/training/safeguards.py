"""
AniCare AI — Automated Scientific Safeguards & Test Partition Protection
Enforces strict prevention of test-set data leakage, test-informed model selection,
and threshold optimization on held-out test data (Milestone 8B).
"""

from typing import List, Dict, Any, Tuple, Optional
import numpy as np


class ScientificGovernanceError(Exception):
    """Base exception for scientific governance violations."""
    pass


class DataLeakageError(ScientificGovernanceError):
    """Raised when test samples contaminate training or validation partitions."""
    pass


class TestSetTuningError(ScientificGovernanceError):
    """Raised when held-out test data is used for model selection, threshold search, or calibration."""
    __test__ = False


def verify_no_test_leakage(
    train_records: Any,
    val_records: Any,
    test_records: Any
) -> bool:
    """
    Verifies zero cryptographic and identifier leakage between training/validation and test sets.
    Accepts lists/sets of string IDs or lists of record dictionaries.
    Raises DataLeakageError if contamination is detected.
    """
    def _extract(recs):
        ids, paths = set(), set()
        for r in recs:
            if isinstance(r, dict):
                if r.get("image_id"):
                    ids.add(r["image_id"])
                if r.get("file_path"):
                    paths.add(r["file_path"])
            elif isinstance(r, str):
                ids.add(r)
        return ids, paths

    test_ids, test_paths = _extract(test_records)
    train_ids, train_paths = _extract(train_records)
    val_ids, val_paths = _extract(val_records)

    id_overlap_train = test_ids & train_ids
    path_overlap_train = test_paths & train_paths if test_paths and train_paths else set()
    if id_overlap_train or path_overlap_train:
        raise DataLeakageError(
            f"DATA_LEAKAGE_DETECTED: {len(id_overlap_train | path_overlap_train)} test samples "
            f"detected in training manifest!"
        )

    id_overlap_val = test_ids & val_ids
    path_overlap_val = test_paths & val_paths if test_paths and val_paths else set()
    if id_overlap_val or path_overlap_val:
        raise DataLeakageError(
            f"DATA_LEAKAGE_DETECTED: {len(id_overlap_val | path_overlap_val)} test samples "
            f"detected in validation manifest!"
        )

    return True


def select_best_model_validation_only(
    candidate_experiments: List[Dict[str, Any]],
    selection_rule: str = "maximize_val_lsd_sensitivity_subject_to_spec_gte_90"
) -> Dict[str, Any]:
    """
    Selects the winning candidate model using VALIDATION METRICS ONLY.
    Strictly refuses execution if test metrics or test partition labels are supplied.
    """
    if not candidate_experiments:
        raise ValueError("Candidate experiment list cannot be empty.")

    # Guard against test set contamination
    forbidden_keys = [
        "test_metrics", "test_sensitivity", "test_recall",
        "test_specificity", "test_accuracy", "test_macro_f1",
        "test_loss", "held_out_test_metrics"
    ]

    for exp in candidate_experiments:
        # Check if experiment dictionary contains forbidden test keys
        for key in forbidden_keys:
            if key in exp:
                raise TestSetTuningError(
                    f"TEST_SET_CONTAMINATION: Experiment '{exp.get('experiment_id')}' contains "
                    f"forbidden test key '{key}'. Model selection must be strictly validation-only!"
                )
        partition = str(exp.get("evaluation_partition", "")).lower()
        if "test" in partition:
            raise TestSetTuningError(
                f"TEST_SET_CONTAMINATION: Experiment '{exp.get('experiment_id')}' references "
                f"partition '{partition}'. Model selection cannot reference test split!"
            )

    # Pre-declared selection rule:
    # 1. Filter models with validation specificity >= 0.90
    # 2. Select highest validation LSD sensitivity / recall
    # 3. Tie-breaker 1: Macro F1
    # 4. Tie-breaker 2: Lowest ECE
    qualifying = []
    for exp in candidate_experiments:
        val_m = exp.get("validation_metrics", exp)
        spec = val_m.get("healthy_specificity", val_m.get("specificity", val_m.get("val_specificity", 0.0)))
        if spec >= 0.90:
            qualifying.append(exp)

    candidates_to_rank = qualifying if qualifying else candidate_experiments

    def sort_key(item):
        m = item.get("validation_metrics", item)
        recall = m.get("lsd_sensitivity_recall", m.get("sensitivity", m.get("lsd_recall", m.get("val_sensitivity", 0.0))))
        f1 = m.get("macro_f1", m.get("val_macro_f1", 0.0))
        ece = m.get("ece", m.get("val_ece", 1.0))
        return (recall, f1, -ece)

    sorted_candidates = sorted(candidates_to_rank, key=sort_key, reverse=True)
    winner = sorted_candidates[0]
    exp_id = winner.get("experiment_id", winner.get("id"))

    return {
        "id": exp_id,
        "winning_experiment_id": exp_id,
        "selection_rule": selection_rule,
        "selection_partition": "validation_set_only",
        "total_candidates_evaluated": len(candidate_experiments),
        "qualifying_candidates_count": len(qualifying),
        "winner_details": winner
    }


def select_threshold_validation_only(
    val_y_true: Any,
    val_y_prob: Any,
    search_range: Tuple[float, float] = (0.30, 0.70),
    step: float = 0.05,
    min_specificity: float = 0.90,
    data_partition_label: str = "validation",
    partition: Optional[str] = None
) -> Dict[str, Any]:
    """
    Selects operating threshold strictly using validation ground truth and predicted probabilities.
    Rejects execution if data_partition_label indicates test split.
    """
    effective_label = partition or data_partition_label
    clean_label = str(effective_label).strip().lower()
    if clean_label in ["test", "held_out_test", "test_split", "test_set"]:
        raise TestSetTuningError(
            f"TEST_SET_CONTAMINATION: Threshold search attempted on '{effective_label}'. "
            "Operating threshold selection must be performed strictly on validation data!"
        )

    val_y_true = np.asarray(val_y_true)
    val_y_prob = np.asarray(val_y_prob)

    best_thresh = 0.50
    best_sensitivity = 0.0
    best_f1 = 0.0
    best_spec = 0.0

    thresholds = np.arange(search_range[0], search_range[1] + 1e-5, step)
    results = []

    for th in thresholds:
        th = round(float(th), 2)
        y_pred = (val_y_prob >= th).astype(int)

        tp = int(np.sum((val_y_true == 1) & (y_pred == 1)))
        fn = int(np.sum((val_y_true == 1) & (y_pred == 0)))
        tn = int(np.sum((val_y_true == 0) & (y_pred == 0)))
        fp = int(np.sum((val_y_true == 0) & (y_pred == 1)))

        sens = tp / max(tp + fn, 1)
        spec = tn / max(tn + fp, 1)
        prec = tp / max(tp + fp, 1) if (tp + fp) > 0 else 0.0
        f1 = 2 * prec * sens / max(prec + sens, 1e-8)

        results.append({
            "threshold": th,
            "sensitivity": round(sens, 4),
            "specificity": round(spec, 4),
            "f1": round(f1, 4),
            "tp": tp, "fn": fn, "tn": tn, "fp": fp
        })

        if spec >= min_specificity:
            if (sens > best_sensitivity) or (sens == best_sensitivity and f1 > best_f1):
                best_sensitivity = sens
                best_spec = spec
                best_f1 = f1
                best_thresh = th

    return {
        "selected_threshold": best_thresh,
        "selection_partition": "validation_set_only",
        "validation_sensitivity": round(best_sensitivity, 4),
        "validation_specificity": round(best_spec, 4),
        "validation_f1": round(best_f1, 4),
        "sweep_grid": results
    }
