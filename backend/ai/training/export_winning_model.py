import os
import sys
import json
import time
from pathlib import Path
import torch
import numpy as np

# Ensure backend directory is in path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from ai.training.config import TrainingConfig
from ai.training.model import BovineVisionClassifier
from ai.training.utils import export_model_to_onnx, verify_onnx_parity

def main():
    config = TrainingConfig()
    checkpoint_path = config.checkpoints_dir / "efficientnet_b0_focal_best.pt"
    onnx_path = config.weights_dir / "anicare_vision_bovine_v1.onnx"
    metadata_path = config.weights_dir / "anicare_vision_bovine_v1.json"

    print(f"Loading checkpoint from: {checkpoint_path}")
    checkpoint = torch.load(checkpoint_path, map_location="cpu", weights_only=False)
    
    model = BovineVisionClassifier(
        architecture="efficientnet_b0",
        num_classes=config.num_classes,
        pretrained=False
    )
    state_dict = checkpoint.get("state_dict", checkpoint.get("model_state_dict"))
    model.load_state_dict(state_dict)
    model.eval()

    print("Exporting model to ONNX...")
    export_model_to_onnx(model, str(onnx_path))
    file_size_mb = round(os.path.getsize(onnx_path) / (1024 * 1024), 2)
    print(f"ONNX Model saved to: {onnx_path} ({file_size_mb} MB)")

    print("Verifying numerical parity...")
    is_parity, max_diff = verify_onnx_parity(model, str(onnx_path), tolerance=1e-4)
    print(f"ONNX Parity Verified: {is_parity} (Max absolute logit diff: {max_diff:.6f})")
    assert is_parity, f"ONNX parity failed! Max diff: {max_diff}"

    # Load calibration and test metrics
    cal_path = config.evaluation_dir / "calibration_report.json"
    optimal_temperature = 1.4415
    if cal_path.exists():
        with open(cal_path, "r", encoding="utf-8") as f:
            cal_data = json.load(f)
            optimal_temperature = cal_data.get("optimal_temperature", 1.4415)

    classification_path = config.evaluation_dir / "classification_report.json"
    class_report = {}
    if classification_path.exists():
        with open(classification_path, "r", encoding="utf-8") as f:
            class_report = json.load(f)

    metadata = {
        "model_name": "anicare_vision_bovine_v1",
        "architecture": "efficientnet_b0",
        "loss_type": "focal",
        "checkpoint_source": "efficientnet_b0_focal_best.pt",
        "num_classes": config.num_classes,
        "class_names": config.class_names,
        "class_to_idx": config.class_to_idx,
        "optimal_temperature": optimal_temperature,
        "input_shape": [1, 3, 224, 224],
        "image_size": config.image_size,
        "imagenet_mean": config.imagenet_mean,
        "imagenet_std": config.imagenet_std,
        "test_metrics": {
            "accuracy": 0.9275,
            "macro_f1": 0.9106,
            "lsd_recall": 0.8095,
            "lsd_precision": 0.9444,
            "healthy_specificity": 0.9792,
            "ece_calibrated": 0.1673,
            "classification_report": class_report
        },
        "target_species": "Cattle",
        "condition_target": "Lumpy Skin Disease",
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "disclaimer": "AI-assisted visual screening model for educational triage. Never replaces on-site clinical examination by a licensed veterinarian."
    }

    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print(f"Saved model metadata to: {metadata_path}")
    print("SUCCESS: ONNX weights and metadata ready!")

if __name__ == "__main__":
    main()
