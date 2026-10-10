"""
AniCare AI — Multi-Class Bovine Disease Classifier Training & Evaluation
Trains a transfer learning model on Task A (Healthy, FMD, LSD) and evaluates on held-out test split.
"""

import os
import sys
import json
import time
import copy
from pathlib import Path
from typing import Dict, Any, List, Tuple
from PIL import Image

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
import torchvision.transforms as transforms
import torchvision.models as models
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, f1_score

# Ensure backend root on sys.path
backend_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_root))

from app.config import settings

RANDOM_SEED = 42
torch.manual_seed(RANDOM_SEED)

CLASS_NAMES = [
    "Healthy / Normal",
    "Foot and Mouth Disease",
    "Lumpy Skin Disease"
]
CLASS_TO_IDX = {name: idx for idx, name in enumerate(CLASS_NAMES)}

class BovineDiseaseDataset(Dataset):
    def __init__(self, items: List[Dict[str, Any]], transform=None):
        self.items = items
        self.transform = transform

    def __len__(self):
        return len(self.items)

    def __getitem__(self, idx):
        item = self.items[idx]
        img_path = item["absolute_path"]
        try:
            image = Image.open(img_path).convert("RGB")
        except Exception:
            # Fallback to black image if unreadable
            image = Image.new("RGB", (224, 224), (0, 0, 0))

        if self.transform:
            image = self.transform(image)

        label = CLASS_TO_IDX.get(item["class_label"], 0)
        return image, label, item["id"]

def get_transforms():
    train_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(10),
        transforms.ColorJitter(brightness=0.1, contrast=0.1),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    eval_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    return train_transform, eval_transform

def train_disease_model(num_epochs: int = 4, batch_size: int = 32):
    manifest_path = Path(settings.DATASETS_MANIFEST_DIR) / "manifest_disease_a.json"
    if not manifest_path.exists():
        manifest_path = backend_root.parent / "backend" / "ai" / "manifests" / "manifest_disease_a.json"
    
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    all_images = manifest["images"]
    train_items = [it for it in all_images if it.get("split") == "train"]
    val_items = [it for it in all_images if it.get("split") == "val"]
    test_items = [it for it in all_images if it.get("split") == "test"]

    print(f"Loaded Task A Dataset: Train={len(train_items)}, Val={len(val_items)}, Test={len(test_items)}")

    train_tf, eval_tf = get_transforms()
    train_loader = DataLoader(BovineDiseaseDataset(train_items, train_tf), batch_size=batch_size, shuffle=True, num_workers=0)
    val_loader = DataLoader(BovineDiseaseDataset(val_items, eval_tf), batch_size=batch_size, shuffle=False, num_workers=0)
    test_loader = DataLoader(BovineDiseaseDataset(test_items, eval_tf), batch_size=batch_size, shuffle=False, num_workers=0)

    device = torch.device("cpu")
    print(f"Using device: {device}")

    # Build model using MobileNetV2 backbone
    model = models.mobilenet_v2(weights=models.MobileNet_V2_Weights.DEFAULT)
    # Freeze earlier layers, fine-tune last blocks + classifier
    for param in model.features[:14].parameters():
        param.requires_grad = False

    in_features = model.classifier[1].in_features
    model.classifier = nn.Sequential(
        nn.Dropout(0.2),
        nn.Linear(in_features, len(CLASS_NAMES))
    )
    model.to(device)

    # Class weights for loss
    class_counts = [0, 0, 0]
    for it in train_items:
        class_counts[CLASS_TO_IDX[it["class_label"]]] += 1
    total_train = len(train_items)
    weights = [total_train / (len(CLASS_NAMES) * max(c, 1)) for c in class_counts]
    class_weights_tensor = torch.tensor(weights, dtype=torch.float32).to(device)
    print(f"Class train distribution: {class_counts}, Loss weights: {[round(w, 2) for w in weights]}")

    criterion = nn.CrossEntropyLoss(weight=class_weights_tensor)
    optimizer = torch.optim.AdamW(filter(lambda p: p.requires_grad, model.parameters()), lr=1e-3, weight_decay=1e-4)

    best_val_f1 = 0.0
    best_model_weights = None
    training_history = []

    print("\nStarting model training...")
    start_time = time.time()

    for epoch in range(1, num_epochs + 1):
        epoch_start = time.time()
        model.train()
        running_loss = 0.0
        train_preds, train_targets = [], []

        for images, labels, _ in train_loader:
            images, labels = images.to(device), labels.to(device)
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item() * images.size(0)
            preds = torch.argmax(outputs, dim=1)
            train_preds.extend(preds.cpu().tolist())
            train_targets.extend(labels.cpu().tolist())

        train_loss = running_loss / len(train_items)
        train_acc = accuracy_score(train_targets, train_preds)
        train_f1 = f1_score(train_targets, train_preds, average="macro")

        # Validation
        model.eval()
        val_loss = 0.0
        val_preds, val_targets = [], []
        with torch.no_grad():
            for images, labels, _ in val_loader:
                images, labels = images.to(device), labels.to(device)
                outputs = model(images)
                loss = criterion(outputs, labels)
                val_loss += loss.item() * images.size(0)
                preds = torch.argmax(outputs, dim=1)
                val_preds.extend(preds.cpu().tolist())
                val_targets.extend(labels.cpu().tolist())

        val_loss = val_loss / len(val_items)
        val_acc = accuracy_score(val_targets, val_preds)
        val_f1 = f1_score(val_targets, val_preds, average="macro")
        epoch_time = time.time() - epoch_start

        print(f"Epoch {epoch}/{num_epochs} [{epoch_time:.1f}s]: Train Loss={train_loss:.4f}, Train F1={train_f1:.4f} | Val Loss={val_loss:.4f}, Val Acc={val_acc:.4f}, Val F1={val_f1:.4f}")

        training_history.append({
            "epoch": epoch,
            "train_loss": round(train_loss, 4),
            "train_accuracy": round(train_acc, 4),
            "train_macro_f1": round(train_f1, 4),
            "val_loss": round(val_loss, 4),
            "val_accuracy": round(val_acc, 4),
            "val_macro_f1": round(val_f1, 4)
        })

        if val_f1 > best_val_f1 or best_model_weights is None:
            best_val_f1 = val_f1
            best_model_weights = copy.deepcopy(model.state_dict())

    print(f"\nTraining completed in {time.time() - start_time:.1f}s. Best Validation Macro F1: {best_val_f1:.4f}")
    model.load_state_dict(best_model_weights)

    # -------------------------------------------------------------
    # Held-Out Test Evaluation
    # -------------------------------------------------------------
    _run_and_save_test_evaluation(model, test_loader, device, len(train_items), len(val_items), len(test_items), training_history, round(time.time() - start_time, 2))


def _run_and_save_test_evaluation(model, test_loader, device, n_train, n_val, n_test, training_history=None, training_time=0.0):
    print("\nEvaluating on held-out test split (15%)...")
    model.eval()
    test_preds, test_targets, test_probs = [], [], []

    with torch.no_grad():
        for images, labels, _ in test_loader:
            images = images.to(device)
            outputs = model(images)
            probs = torch.softmax(outputs, dim=1)
            preds = torch.argmax(outputs, dim=1)

            test_preds.extend(preds.cpu().tolist())
            test_targets.extend(labels.tolist())
            test_probs.extend(probs.cpu().tolist())

    test_acc = accuracy_score(test_targets, test_preds)
    test_macro_f1 = f1_score(test_targets, test_preds, average="macro")
    test_weighted_f1 = f1_score(test_targets, test_preds, average="weighted")
    cm = confusion_matrix(test_targets, test_preds).tolist()
    report = classification_report(test_targets, test_preds, target_names=CLASS_NAMES, output_dict=True)

    print(f"Test Accuracy:    {test_acc * 100:.2f}%")
    print(f"Test Macro F1:    {test_macro_f1:.4f}")
    print(f"Test Weighted F1: {test_weighted_f1:.4f}")
    print("Confusion Matrix:")
    for row in cm:
        print(" ", row)

    # Save artifacts
    weights_dir = backend_root / "ai" / "models" / "weights"
    weights_dir.mkdir(parents=True, exist_ok=True)
    eval_dir = backend_root / "ai" / "models" / "evaluation"
    eval_dir.mkdir(parents=True, exist_ok=True)

    pt_save_path = weights_dir / "disease_classifier_multiclass_v1.pt"
    json_meta_path = weights_dir / "disease_classifier_multiclass_v1.json"
    eval_report_path = eval_dir / "multi_disease_metrics.json"

    # Save PyTorch checkpoint
    torch.save({
        "state_dict": model.state_dict(),
        "architecture": "mobilenet_v2",
        "num_classes": len(CLASS_NAMES),
        "class_names": CLASS_NAMES,
        "class_to_idx": CLASS_TO_IDX,
        "input_size": [3, 224, 224]
    }, pt_save_path)
    print(f"Saved PyTorch model: {pt_save_path}")

    # Build metadata & metrics JSON
    meta_data = {
        "model_name": "disease_classifier_multiclass_v1",
        "model_version": "AniCare-MultiDisease-Vision v1.0",
        "task": "Task A: Bovine Disease Classification",
        "architecture": "mobilenet_v2",
        "num_classes": 3,
        "class_names": CLASS_NAMES,
        "class_to_idx": CLASS_TO_IDX,
        "dataset_sources": ["FMD_Cattle", "Cows Disease Dataset (archive)"],
        "dataset_manifest": "backend/ai/manifests/manifest_disease_a.json",
        "hardware": "cpu",
        "train_samples": n_train,
        "val_samples": n_val,
        "test_samples": n_test,
        "test_metrics": {
            "accuracy": round(test_acc, 4),
            "macro_f1": round(test_macro_f1, 4),
            "weighted_f1": round(test_weighted_f1, 4),
            "confusion_matrix": cm,
            "classification_report": report
        },
        "training_history": training_history or [],
        "training_time_seconds": training_time,
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "disclaimer": "AI-assisted screening triage. Never replaces on-site clinical examination by a licensed veterinarian."
    }

    with open(json_meta_path, "w", encoding="utf-8") as f:
        json.dump(meta_data, f, indent=2)
    with open(eval_report_path, "w", encoding="utf-8") as f:
        json.dump(meta_data, f, indent=2)

    print(f"Saved Metadata & Test Metrics: {json_meta_path}")
    print("[SUCCESS] Multi-Class Bovine Disease Classifier evaluation complete!")


def evaluate_disease_model():
    manifest_path = Path(settings.DATASETS_MANIFEST_DIR) / "manifest_disease_a.json"
    if not manifest_path.exists():
        manifest_path = backend_root.parent / "backend" / "ai" / "manifests" / "manifest_disease_a.json"
    
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    all_images = manifest["images"]
    train_items = [it for it in all_images if it.get("split") == "train"]
    val_items = [it for it in all_images if it.get("split") == "val"]
    test_items = [it for it in all_images if it.get("split") == "test"]

    print(f"Evaluating model on Task A: Train={len(train_items)}, Val={len(val_items)}, Test={len(test_items)}")

    _, eval_tf = get_transforms()
    test_loader = DataLoader(BovineDiseaseDataset(test_items, eval_tf), batch_size=32, shuffle=False, num_workers=0)
    device = torch.device("cpu")

    weights_path = backend_root / "ai" / "models" / "weights" / "disease_classifier_multiclass_v1.pt"
    if not weights_path.is_file():
        raise FileNotFoundError(f"Trained model not found at {weights_path}")

    checkpoint = torch.load(weights_path, map_location=device, weights_only=False)
    model = models.mobilenet_v2(weights=None)
    in_features = model.classifier[1].in_features
    model.classifier = nn.Sequential(
        nn.Dropout(0.2),
        nn.Linear(in_features, len(CLASS_NAMES))
    )
    model.load_state_dict(checkpoint["state_dict"])
    model.to(device)

    # Load existing training history if available
    meta_path = weights_path.with_suffix(".json")
    training_history = []
    training_time = 0.0
    if meta_path.is_file():
        with open(meta_path, "r", encoding="utf-8") as f:
            m = json.load(f)
            training_history = m.get("training_history", [])
            training_time = m.get("training_time_seconds", 0.0)

    _run_and_save_test_evaluation(
        model, test_loader, device,
        len(train_items), len(val_items), len(test_items),
        training_history, training_time
    )


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="AniCare AI Multi-Class Disease Classifier")
    parser.add_argument("--eval-only", action="store_true", help="Evaluate existing checkpoint on held-out test split")
    parser.add_argument("--resume", action="store_true", help="Resume training from existing weights")
    parser.add_argument("--epochs", type=int, default=4, help="Number of training epochs")
    parser.add_argument("--batch-size", type=int, default=32, help="Batch size")
    args = parser.parse_args()

    if args.eval_only:
        evaluate_disease_model()
    else:
        train_disease_model(num_epochs=args.epochs, batch_size=args.batch_size)
