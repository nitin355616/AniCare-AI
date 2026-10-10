"""
AniCare AI — Training Utilities, Plotting & ONNX Parity Verification
"""

import os
import random
from typing import List, Tuple
import numpy as np
import torch
import torch.nn as nn
import matplotlib
matplotlib.use("Agg")  # Headless backend
import matplotlib.pyplot as plt
import onnx
import onnxruntime as ort


def set_seed(seed: int = 42) -> None:
    """Guarantees strict determinism across Python, NumPy, and PyTorch CPU."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False


def plot_and_save_confusion_matrix(
    cm_matrix: List[List[int]],
    class_names: List[str],
    save_path: str,
    title: str = "AniCare AI — Lumpy Skin Disease Confusion Matrix"
) -> None:
    """Renders high-resolution confusion matrix plot and saves to disk."""
    cm = np.array(cm_matrix)
    fig, ax = plt.subplots(figsize=(6, 5), dpi=300)

    # Row-normalize to show per-class recall
    cm_norm = cm.astype("float") / cm.sum(axis=1)[:, np.newaxis]

    cax = ax.matshow(cm_norm, cmap=plt.cm.Blues, vmin=0, vmax=1)
    fig.colorbar(cax)

    ax.set_xticks(range(len(class_names)))
    ax.set_yticks(range(len(class_names)))
    ax.set_xticklabels(class_names, rotation=20, ha="left", fontsize=9)
    ax.set_yticklabels(class_names, fontsize=9)

    ax.set_xlabel("Predicted Condition", labelpad=10, fontweight="bold")
    ax.set_ylabel("True Condition", labelpad=10, fontweight="bold")
    ax.set_title(title, pad=20, fontsize=11, fontweight="bold")

    # Annotate cells with both count and percentage
    for i in range(len(class_names)):
        for j in range(len(class_names)):
            count = cm[i, j]
            pct = cm_norm[i, j] * 100
            color = "white" if cm_norm[i, j] > 0.5 else "black"
            ax.text(j, i, f"{count}\n({pct:.1f}%)", ha="center", va="center", color=color, fontsize=10)

    plt.tight_layout()
    os.makedirs(os.path.dirname(os.path.abspath(save_path)), exist_ok=True)
    plt.savefig(save_path)
    plt.close()


def export_model_to_onnx(
    model: nn.Module,
    save_path: str,
    input_shape: Tuple[int, int, int, int] = (1, 3, 224, 224)
) -> str:
    """Exports PyTorch model to standard ONNX graph format."""
    model.eval()
    dummy_input = torch.randn(*input_shape)
    os.makedirs(os.path.dirname(os.path.abspath(save_path)), exist_ok=True)

    torch.onnx.export(
        model,
        dummy_input,
        save_path,
        export_params=True,
        opset_version=14,
        do_constant_folding=True,
        input_names=["input"],
        output_names=["logits"],
        dynamic_axes={
            "input": {0: "batch_size"},
            "logits": {0: "batch_size"}
        },
        dynamo=False
    )

    # Validate ONNX model definition
    onnx_model = onnx.load(save_path)
    onnx.checker.check_model(onnx_model)
    return save_path


def verify_onnx_parity(
    pytorch_model: nn.Module,
    onnx_path: str,
    tolerance: float = 1e-4
) -> Tuple[bool, float]:
    """Verifies numerical parity between PyTorch and ONNX Runtime predictions."""
    pytorch_model.eval()
    test_input = torch.randn(2, 3, 224, 224)

    with torch.no_grad():
        torch_logits = pytorch_model(test_input).numpy()

    session = ort.InferenceSession(onnx_path, providers=["CPUExecutionProvider"])
    ort_inputs = {session.get_inputs()[0].name: test_input.numpy()}
    ort_logits = session.run(None, ort_inputs)[0]

    max_diff = float(np.max(np.abs(torch_logits - ort_logits)))
    is_parity = bool(max_diff < tolerance)
    return is_parity, max_diff
