"""
AniCare AI — Milestone 5 Master Benchmark & Evaluation Runner
Trains MobileNetV3-Large and EfficientNet-B0 under Focal Loss and Weighted Cross-Entropy.
Selects best model via validation metrics, calibrates confidence, evaluates on untouched test split,
and exports verified ONNX model graph.
"""

import os
import sys
import json
import time
from pathlib import Path
from typing import Dict, Any, List
import numpy as np
import torch
import torch.nn as nn

# Ensure backend root on sys.path
backend_root = Path(__file__).resolve().parent.parent.parent
if str(backend_root) not in sys.path:
    sys.path.insert(0, str(backend_root))

from ai.training.config import TrainingConfig
from ai.training.dataset import create_dataloaders
from ai.training.train import train_model
from ai.training.evaluate import evaluate_dataloader
from ai.training.calibration import ModelTemperatureScaler, compute_ece
from ai.training.utils import (
    set_seed,
    plot_and_save_confusion_matrix,
    export_model_to_onnx,
    verify_onnx_parity
)


def run_full_benchmark():
    config = TrainingConfig()
    set_seed(config.seed)

    print("\n" + "=" * 70)
    print("ANICARE AI — MILESTONE 5: VISION MODEL BENCHMARK & EVALUATION")
    print("=" * 70)
    print(f"Device: {config.device}")
    print(f"Seed: {config.seed}")
    print(f"Classes: {config.class_names}")

    # Create DataLoaders
    train_loader, val_loader, test_loader, data_meta = create_dataloaders(config)
    print(f"Class frequency weights: {data_meta['class_weights']}")
    print(f"Focal alpha weights: {data_meta['focal_alpha']}")

    # Benchmark candidates to train and evaluate on validation set
    candidates = [
        {"arch": "mobilenet_v3_large", "loss": "focal"},
        {"arch": "mobilenet_v3_large", "loss": "weighted_ce"},
        {"arch": "efficientnet_b0", "loss": "focal"},
        {"arch": "efficientnet_b0", "loss": "weighted_ce"},
    ]

    benchmark_val_results = []
    trained_models = {}

    for cand in candidates:
        arch = cand["arch"]
        loss_name = cand["loss"]
        key = f"{arch}_{loss_name}"

        # Train model on Train partition, save best validation checkpoint
        model, best_val_metrics, history = train_model(
            architecture=arch,
            loss_type=loss_name,
            train_loader=train_loader,
            val_loader=val_loader,
            data_meta=data_meta,
            config=config
        )

        # Measure CPU inference latency on validation batch
        dummy_input = torch.randn(1, 3, 224, 224).to(config.device)
        model.eval()
        # Warmup
        for _ in range(10):
            _ = model(dummy_input)
        latencies = []
        for _ in range(50):
            t0 = time.perf_counter()
            _ = model(dummy_input)
            latencies.append((time.perf_counter() - t0) * 1000)
        avg_latency_ms = round(float(np.mean(latencies)), 2)

        # Measure parameter count and checkpoint size
        trainable_p, total_p = model.count_trainable_parameters()
        ckpt_path = config.checkpoints_dir / f"{key}_best.pt"
        ckpt_size_mb = round(os.path.getsize(ckpt_path) / (1024 * 1024), 2)

        cand_result = {
            "key": key,
            "architecture": arch,
            "loss_type": loss_name,
            "val_accuracy": best_val_metrics["accuracy"],
            "val_macro_f1": best_val_metrics["macro_f1"],
            "val_lsd_recall": best_val_metrics["lsd_sensitivity_recall"],
            "val_lsd_precision": best_val_metrics["lsd_precision"],
            "val_healthy_specificity": best_val_metrics["healthy_specificity"],
            "val_ece": best_val_metrics["ece"],
            "avg_cpu_latency_ms": avg_latency_ms,
            "parameters_total": total_p,
            "checkpoint_size_mb": ckpt_size_mb,
            "best_val_metrics": best_val_metrics
        }
        benchmark_val_results.append(cand_result)
        trained_models[key] = model

    # =========================================================================
    # MODEL SELECTION (Strictly Based on Validation Performance)
    # =========================================================================
    print("\n" + "=" * 70)
    print("VALIDATION BENCHMARK COMPARISON TABLE")
    print("=" * 70)
    print(f"{'Model Key':<28} | {'Val F1':<8} | {'LSD Recall':<10} | {'Specificity':<11} | {'ECE':<6} | {'Latency':<8} | {'Size':<6}")
    print("-" * 85)
    for r in benchmark_val_results:
        print(
            f"{r['key']:<28} | {r['val_macro_f1']:<8.3f} | {r['val_lsd_recall']:<10.3f} | "
            f"{r['val_healthy_specificity']:<11.3f} | {r['val_ece']:<6.3f} | {r['avg_cpu_latency_ms']:<6.1f}ms | {r['checkpoint_size_mb']:<6.1f}MB"
        )

    # Selection sorting: 1. LSD Recall (high), 2. Macro F1 (high), 3. ECE (low), 4. Latency (low)
    # Clinical rule: Prioritize detecting sick animals (LSD recall) without sacrificing Macro F1
    sorted_candidates = sorted(
        benchmark_val_results,
        key=lambda x: (x["val_lsd_recall"], x["val_macro_f1"], -x["val_ece"], -x["avg_cpu_latency_ms"]),
        reverse=True
    )
    winning_candidate = sorted_candidates[0]
    winning_key = winning_candidate["key"]
    winning_model = trained_models[winning_key]

    print("\n" + "=" * 70)
    print(f"SELECTED WINNING MODEL: {winning_key}")
    print(f"Reason: Top validation performance (LSD Recall: {winning_candidate['val_lsd_recall']:.3f}, Macro F1: {winning_candidate['val_macro_f1']:.3f})")
    print("=" * 70)

    # =========================================================================
    # CONFIDENCE CALIBRATION ON VALIDATION SPLIT
    # =========================================================================
    print("\n--- Fitting Temperature Scaler on Validation Logits ---")
    winning_model.eval()
    val_logits_list = []
    val_targets_list = []
    with torch.no_grad():
        for imgs, tgts, _, _ in val_loader:
            val_logits_list.append(winning_model(imgs))
            val_targets_list.append(tgts)
    val_logits = torch.cat(val_logits_list, dim=0)
    val_targets = torch.cat(val_targets_list, dim=0)

    temp_scaler = ModelTemperatureScaler()
    optimal_temperature = temp_scaler.fit(val_logits, val_targets)
    print(f"Optimal Temperature (T): {optimal_temperature:.4f}")

    # Uncalibrated vs Calibrated ECE on validation set
    val_probs_uncal = torch.softmax(val_logits, dim=1).numpy()
    val_probs_cal = torch.softmax(val_logits / optimal_temperature, dim=1).numpy()
    ece_val_uncal, _ = compute_ece(val_probs_uncal, val_targets.numpy())
    ece_val_cal, cal_bins = compute_ece(val_probs_cal, val_targets.numpy())
    print(f"Validation ECE Before Calibration: {ece_val_uncal:.4f}")
    print(f"Validation ECE After Calibration:  {ece_val_cal:.4f}")

    # =========================================================================
    # FINAL EVALUATION: ONCE ON UNTOUCHED TEST SPLIT
    # =========================================================================
    print("\n" + "=" * 70)
    print("FINAL EVALUATION ON UNTOUCHED TEST PARTITION (138 Images)")
    print("=" * 70)

    test_metrics, test_true, test_pred, test_probs, failure_cases = evaluate_dataloader(
        winning_model,
        test_loader,
        config.class_names,
        device=config.device,
        temperature=optimal_temperature
    )

    print(f"Test Accuracy:             {test_metrics['accuracy'] * 100:.2f}%")
    print(f"Test Macro F1:             {test_metrics['macro_f1']:.4f}")
    print(f"Test LSD Recall (Sens.):   {test_metrics['lsd_sensitivity_recall'] * 100:.2f}%")
    print(f"Test LSD Precision:        {test_metrics['lsd_precision'] * 100:.2f}%")
    print(f"Test Healthy Specificity:  {test_metrics['healthy_specificity'] * 100:.2f}%")
    print(f"Test ROC-AUC:              {test_metrics['roc_auc']:.4f}")
    print(f"Test PR-AUC:               {test_metrics['pr_auc']:.4f}")
    print(f"Test ECE (Calibrated):     {test_metrics['ece']:.4f}")
    print(f"Confusion Matrix:          {test_metrics['confusion_matrix']['raw_matrix']}")
    print(f"False Negatives (Missed):  {test_metrics['false_negatives_count']}")
    print(f"False Positives:           {test_metrics['false_positives_count']}")

    # Save artifacts in backend/ai/models/evaluation/
    os.makedirs(config.evaluation_dir, exist_ok=True)

    # 1. Confusion Matrix Plot
    cm_plot_path = config.evaluation_dir / "confusion_matrix.png"
    plot_and_save_confusion_matrix(
        test_metrics["confusion_matrix"]["raw_matrix"],
        config.class_names,
        str(cm_plot_path),
        title=f"AniCare AI — {winning_candidate['architecture']} (Test Set)"
    )
    print(f"Saved confusion matrix plot to: {cm_plot_path}")

    # 2. Metrics JSON
    metrics_json_path = config.evaluation_dir / "metrics.json"
    full_metrics_export = {
        "selected_model": winning_candidate,
        "optimal_temperature": optimal_temperature,
        "validation_benchmark_comparison": benchmark_val_results,
        "final_test_metrics": test_metrics
    }
    with open(metrics_json_path, "w", encoding="utf-8") as f:
        json.dump(full_metrics_export, f, indent=2)

    # 3. Classification Report JSON
    class_report_path = config.evaluation_dir / "classification_report.json"
    with open(class_report_path, "w", encoding="utf-8") as f:
        json.dump(test_metrics["per_class"], f, indent=2)

    # 4. Calibration Report JSON
    calibration_report_path = config.evaluation_dir / "calibration_report.json"
    with open(calibration_report_path, "w", encoding="utf-8") as f:
        json.dump({
            "optimal_temperature": optimal_temperature,
            "validation_ece_before": ece_val_uncal,
            "validation_ece_after": ece_val_cal,
            "test_ece_calibrated": test_metrics["ece"],
            "test_calibration_bins": test_metrics["ece_details"]
        }, f, indent=2)

    # 5. Failure Cases JSON
    failure_cases_path = config.evaluation_dir / "failure_cases.json"
    with open(failure_cases_path, "w", encoding="utf-8") as f:
        json.dump({
            "total_failures": len(failure_cases),
            "false_negatives": [f for f in failure_cases if f["failure_type"] == "FALSE_NEGATIVE_MISSED_LSD"],
            "false_positives": [f for f in failure_cases if f["failure_type"] == "FALSE_POSITIVE_FALSE_ALARM"],
        }, f, indent=2)

    # =========================================================================
    # EXPORT WINNING MODEL TO ONNX
    # =========================================================================
    print("\n" + "=" * 70)
    print("EXPORTING SELECTED MODEL TO ONNX GRAPH")
    print("=" * 70)

    onnx_path = config.weights_dir / "anicare_vision_bovine_v1.onnx"
    export_model_to_onnx(winning_model, str(onnx_path))
    onnx_file_size_mb = round(os.path.getsize(onnx_path) / (1024 * 1024), 2)
    print(f"Exported ONNX model to: {onnx_path} ({onnx_file_size_mb} MB)")

    # Verify numerical parity between PyTorch and ONNX Runtime
    is_parity, max_diff = verify_onnx_parity(winning_model, str(onnx_path), tolerance=1e-4)
    print(f"ONNX Parity Verified: {is_parity} (Max absolute logit diff: {max_diff:.6f})")
    assert is_parity, f"ONNX parity check failed! Max diff: {max_diff}"

    # Also save model metadata alongside weights
    model_metadata = {
        "model_name": "anicare_vision_bovine_v1",
        "architecture": winning_candidate["architecture"],
        "loss_type": winning_candidate["loss_type"],
        "num_classes": config.num_classes,
        "class_names": config.class_names,
        "class_to_idx": config.class_to_idx,
        "optimal_temperature": optimal_temperature,
        "input_shape": [1, 3, 224, 224],
        "image_size": config.image_size,
        "imagenet_mean": config.imagenet_mean,
        "imagenet_std": config.imagenet_std,
        "test_metrics": {
            "accuracy": test_metrics["accuracy"],
            "macro_f1": test_metrics["macro_f1"],
            "lsd_recall": test_metrics["lsd_sensitivity_recall"],
            "lsd_precision": test_metrics["lsd_precision"],
            "healthy_specificity": test_metrics["healthy_specificity"],
            "ece": test_metrics["ece"]
        },
        "target_species": "Cattle",
        "condition_target": "Lumpy Skin Disease",
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "disclaimer": "AI-assisted visual screening model for educational triage. Never replaces on-site clinical examination by a licensed veterinarian."
    }
    with open(config.weights_dir / "anicare_vision_bovine_v1.json", "w", encoding="utf-8") as f:
        json.dump(model_metadata, f, indent=2)

    print("\n" + "=" * 70)
    print("BENCHMARK & EXPORT FULLY COMPLETED")
    print("=" * 70)
    return full_metrics_export


if __name__ == "__main__":
    run_full_benchmark()
