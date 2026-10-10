"""
AniCare AI — Two-Phase Model Training & Fine-Tuning Engine
Executes Phase 1 (head training) and Phase 2 (fine-tuning) with early stopping and checkpointing.
"""

import os
import time
from pathlib import Path
from typing import Dict, Any, Tuple, List
import copy
import torch
import torch.nn as nn
import torch.optim as optim
from torch.optim.lr_scheduler import CosineAnnealingLR
from torch.utils.data import DataLoader

try:
    from ai.training.config import TrainingConfig
    from ai.training.model import build_model, BovineVisionClassifier
    from ai.training.losses import create_criterion
    from ai.training.evaluate import evaluate_dataloader
    from ai.training.utils import set_seed
except ImportError:
    from backend.ai.training.config import TrainingConfig
    from backend.ai.training.model import build_model, BovineVisionClassifier
    from backend.ai.training.losses import create_criterion
    from backend.ai.training.evaluate import evaluate_dataloader
    from backend.ai.training.utils import set_seed


def train_model(
    architecture: str,
    loss_type: str,
    train_loader: DataLoader,
    val_loader: DataLoader,
    data_meta: Dict[str, Any],
    config: TrainingConfig
) -> Tuple[BovineVisionClassifier, Dict[str, Any], List[Dict[str, Any]]]:
    """
    Executes reproducible two-phase training loop.
    Never evaluates or peeks at the test partition during training or model selection.
    """
    set_seed(config.seed)
    device = config.device

    print(f"\n{'='*60}")
    print(f"TRAINING: {architecture} | Loss: {loss_type}")
    print(f"{'='*60}")

    model = build_model(architecture=architecture, num_classes=config.num_classes, pretrained=True)
    model.to(device)

    criterion = create_criterion(
        loss_type=loss_type,
        class_weights=data_meta["class_weights"],
        focal_alpha=data_meta["focal_alpha"],
        gamma=config.focal_gamma,
        device=device
    )

    best_val_score = -1.0
    best_val_metrics = {}
    best_weights = copy.deepcopy(model.state_dict())
    history: List[Dict[str, Any]] = []

    # =========================================================================
    # PHASE 1: Train Head Only (Backbone Frozen)
    # =========================================================================
    print(f"--- Phase 1: Training Head ({config.phase1_epochs} epochs, lr={config.phase1_lr}) ---")
    model.freeze_backbone()
    trainable_p, total_p = model.count_trainable_parameters()
    print(f"Trainable parameters: {trainable_p:,} / {total_p:,}")

    optimizer_p1 = optim.AdamW(
        [p for p in model.parameters() if p.requires_grad],
        lr=config.phase1_lr,
        weight_decay=config.weight_decay
    )
    scheduler_p1 = CosineAnnealingLR(optimizer_p1, T_max=config.phase1_epochs, eta_min=1e-5)

    for epoch in range(1, config.phase1_epochs + 1):
        model.train()
        total_loss = 0.0
        n_samples = 0

        for images, targets, _, _ in train_loader:
            images = images.to(device)
            targets = targets.to(device)

            optimizer_p1.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, targets)
            loss.backward()
            optimizer_p1.step()

            total_loss += loss.item() * images.size(0)
            n_samples += images.size(0)

        scheduler_p1.step()
        train_loss = total_loss / max(n_samples, 1)

        val_metrics, _, _, _, _ = evaluate_dataloader(model, val_loader, config.class_names, device=device)
        # Selection criterion: Macro F1 + LSD sensitivity (prioritizing detection of sick animals)
        selection_score = val_metrics["macro_f1"] * 0.5 + val_metrics["lsd_sensitivity_recall"] * 0.5

        history.append({
            "phase": 1,
            "epoch": epoch,
            "train_loss": round(train_loss, 4),
            "val_accuracy": val_metrics["accuracy"],
            "val_macro_f1": val_metrics["macro_f1"],
            "val_lsd_recall": val_metrics["lsd_sensitivity_recall"],
            "val_ece": val_metrics["ece"]
        })

        print(
            f"Epoch {epoch:02d} [P1] | Loss: {train_loss:.4f} | "
            f"Val Acc: {val_metrics['accuracy']:.3f} | Macro F1: {val_metrics['macro_f1']:.3f} | "
            f"LSD Recall: {val_metrics['lsd_sensitivity_recall']:.3f} | ECE: {val_metrics['ece']:.3f}"
        )

        if selection_score > best_val_score:
            best_val_score = selection_score
            best_val_metrics = copy.deepcopy(val_metrics)
            best_weights = copy.deepcopy(model.state_dict())

    # =========================================================================
    # PHASE 2: Fine-Tuning Upper Backbone Layers
    # =========================================================================
    print(f"\n--- Phase 2: Fine-Tuning Top Layers ({config.phase2_epochs} epochs, lr={config.phase2_lr}) ---")
    model.unfreeze_top_layers()
    trainable_p2, total_p2 = model.count_trainable_parameters()
    print(f"Trainable parameters: {trainable_p2:,} / {total_p2:,}")

    optimizer_p2 = optim.AdamW(
        [p for p in model.parameters() if p.requires_grad],
        lr=config.phase2_lr,
        weight_decay=config.weight_decay
    )
    scheduler_p2 = CosineAnnealingLR(optimizer_p2, T_max=config.phase2_epochs, eta_min=1e-6)

    epochs_without_improvement = 0

    for epoch in range(1, config.phase2_epochs + 1):
        model.train()
        total_loss = 0.0
        n_samples = 0

        for images, targets, _, _ in train_loader:
            images = images.to(device)
            targets = targets.to(device)

            optimizer_p2.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, targets)
            loss.backward()
            optimizer_p2.step()

            total_loss += loss.item() * images.size(0)
            n_samples += images.size(0)

        scheduler_p2.step()
        train_loss = total_loss / max(n_samples, 1)

        val_metrics, _, _, _, _ = evaluate_dataloader(model, val_loader, config.class_names, device=device)
        selection_score = val_metrics["macro_f1"] * 0.5 + val_metrics["lsd_sensitivity_recall"] * 0.5

        history.append({
            "phase": 2,
            "epoch": config.phase1_epochs + epoch,
            "train_loss": round(train_loss, 4),
            "val_accuracy": val_metrics["accuracy"],
            "val_macro_f1": val_metrics["macro_f1"],
            "val_lsd_recall": val_metrics["lsd_sensitivity_recall"],
            "val_ece": val_metrics["ece"]
        })

        print(
            f"Epoch {epoch:02d} [P2] | Loss: {train_loss:.4f} | "
            f"Val Acc: {val_metrics['accuracy']:.3f} | Macro F1: {val_metrics['macro_f1']:.3f} | "
            f"LSD Recall: {val_metrics['lsd_sensitivity_recall']:.3f} | ECE: {val_metrics['ece']:.3f}"
        )

        if selection_score > best_val_score:
            best_val_score = selection_score
            best_val_metrics = copy.deepcopy(val_metrics)
            best_weights = copy.deepcopy(model.state_dict())
            epochs_without_improvement = 0
        else:
            epochs_without_improvement += 1
            if epochs_without_improvement >= config.early_stopping_patience:
                print(f"Early stopping triggered at Phase 2 epoch {epoch} (patience={config.early_stopping_patience}).")
                break

    # Load and save best validation checkpoint
    model.load_state_dict(best_weights)
    checkpoint_name = f"{architecture}_{loss_type}_best.pt"
    checkpoint_path = config.checkpoints_dir / checkpoint_name
    os.makedirs(config.checkpoints_dir, exist_ok=True)
    torch.save({
        "architecture": architecture,
        "loss_type": loss_type,
        "state_dict": model.state_dict(),
        "best_val_metrics": best_val_metrics,
        "config": config.__dict__
    }, checkpoint_path)
    print(f"Best checkpoint saved to: {checkpoint_path}")

    return model, best_val_metrics, history
