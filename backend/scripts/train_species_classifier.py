"""
AniCare AI — Species Classification Model Training & Evaluation
Trains a transfer learning model for Task B (Cattle, Dog, Cat, Bird) and evaluates on held-out test split.
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

SPECIES_NAMES = [
    "Cattle",
    "Dog",
    "Cat",
    "Bird"
]
SPECIES_TO_IDX = {name: idx for idx, name in enumerate(SPECIES_NAMES)}

class SpeciesDataset(Dataset):
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
            image = Image.new("RGB", (224, 224), (0, 0, 0))

        if self.transform:
            image = self.transform(image)

        label = SPECIES_TO_IDX.get(item["class_label"], 0)
        return image, label, item["id"]

def get_transforms():
    train_tf = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(10),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    eval_tf = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    return train_tf, eval_tf

def train_species_model(num_epochs: int = 3, batch_size: int = 32):
    manifest_path = Path(settings.DATASETS_MANIFEST_DIR) / "manifest_species_b.json"
    if not manifest_path.exists():
        manifest_path = backend_root.parent / "backend" / "ai" / "manifests" / "manifest_species_b.json"

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    all_images = manifest["images"]
    train_items = [it for it in all_images if it.get("split") == "train"]
    val_items = [it for it in all_images if it.get("split") == "val"]
    test_items = [it for it in all_images if it.get("split") == "test"]

    print(f"Loaded Task B Species Dataset: Train={len(train_items)}, Val={len(val_items)}, Test={len(test_items)}")

    train_tf, eval_tf = get_transforms()
    train_loader = DataLoader(SpeciesDataset(train_items, train_tf), batch_size=batch_size, shuffle=True, num_workers=0)
    val_loader = DataLoader(SpeciesDataset(val_items, eval_tf), batch_size=batch_size, shuffle=False, num_workers=0)
    test_loader = DataLoader(SpeciesDataset(test_items, eval_tf), batch_size=batch_size, shuffle=False, num_workers=0)

    device = torch.device("cpu")
    model = models.mobilenet_v2(weights=models.MobileNet_V2_Weights.DEFAULT)
    for param in model.features[:14].parameters():
        param.requires_grad = False

    in_features = model.classifier[1].in_features
    model.classifier = nn.Sequential(
        nn.Dropout(0.2),
        nn.Linear(in_features, len(SPECIES_NAMES))
    )
    model.to(device)

    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.AdamW(filter(lambda p: p.requires_grad, model.parameters()), lr=1e-3, weight_decay=1e-4)

    best_val_f1 = 0.0
    best_weights = None
    training_history = []
    start_time = time.time()

    print("\nTraining Species Classifier...")
    for epoch in range(1, num_epochs + 1):
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

        print(f"Epoch {epoch}/{num_epochs}: Train F1={train_f1:.4f} | Val Loss={val_loss:.4f}, Val Acc={val_acc:.4f}, Val F1={val_f1:.4f}")

        training_history.append({
            "epoch": epoch,
            "train_loss": round(train_loss, 4),
            "train_accuracy": round(train_acc, 4),
            "val_loss": round(val_loss, 4),
            "val_accuracy": round(val_acc, 4),
            "val_macro_f1": round(val_f1, 4)
        })

        if val_f1 > best_val_f1 or best_weights is None:
            best_val_f1 = val_f1
            best_weights = copy.deepcopy(model.state_dict())

    model.load_state_dict(best_weights)

    # Test Evaluation
    model.eval()
    test_preds, test_targets = [], []
    with torch.no_grad():
        for images, labels, _ in test_loader:
            images = images.to(device)
            outputs = model(images)
            preds = torch.argmax(outputs, dim=1)
            test_preds.extend(preds.cpu().tolist())
            test_targets.extend(labels.tolist())

    test_acc = accuracy_score(test_targets, test_preds)
    test_macro_f1 = f1_score(test_targets, test_preds, average="macro")
    test_weighted_f1 = f1_score(test_targets, test_preds, average="weighted")
    cm = confusion_matrix(test_targets, test_preds).tolist()
    report = classification_report(test_targets, test_preds, target_names=SPECIES_NAMES, output_dict=True)

    print(f"\nSpecies Test Accuracy: {test_acc * 100:.2f}% | Macro F1: {test_macro_f1:.4f}")

    weights_dir = backend_root / "ai" / "models" / "weights"
    eval_dir = backend_root / "ai" / "models" / "evaluation"
    weights_dir.mkdir(parents=True, exist_ok=True)
    eval_dir.mkdir(parents=True, exist_ok=True)

    pt_path = weights_dir / "species_classifier_v1.pt"
    onnx_path = weights_dir / "species_classifier_v1.onnx"
    json_path = weights_dir / "species_classifier_v1.json"

    torch.save({
        "state_dict": model.state_dict(),
        "architecture": "mobilenet_v2",
        "num_classes": len(SPECIES_NAMES),
        "class_names": SPECIES_NAMES,
        "class_to_idx": SPECIES_TO_IDX
    }, pt_path)

    try:
        dummy_input = torch.randn(1, 3, 224, 224, device=device)
        torch.onnx.export(
            model,
            dummy_input,
            onnx_path,
            export_params=True,
            opset_version=14,
            do_constant_folding=True,
            input_names=["input"],
            output_names=["output"],
            dynamic_axes={"input": {0: "batch_size"}, "output": {0: "batch_size"}}
        )
    except Exception as e:
        print(f"ONNX export note: {e}")

    meta = {
        "model_name": "species_classifier_v1",
        "model_version": "AniCare-Species-Guard v1.0",
        "task": "Task B: Animal Species Classification",
        "architecture": "mobilenet_v2",
        "num_classes": 4,
        "class_names": SPECIES_NAMES,
        "class_to_idx": SPECIES_TO_IDX,
        "dataset_source": "Class3 Animal Species & Breeds Dataset",
        "train_samples": len(train_items),
        "val_samples": len(val_items),
        "test_samples": len(test_items),
        "test_metrics": {
            "accuracy": round(test_acc, 4),
            "macro_f1": round(test_macro_f1, 4),
            "weighted_f1": round(test_weighted_f1, 4),
            "confusion_matrix": cm,
            "classification_report": report
        },
        "training_history": training_history,
        "training_time_seconds": round(time.time() - start_time, 2),
        "disclaimer": "Validates species before veterinary disease diagnosis."
    }
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)
    with open(eval_dir / "species_metrics.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

    print(f"Saved Species Classifier artifacts: {pt_path}, {json_path}")
    print("[SUCCESS] Species Classifier trained and evaluated!")

if __name__ == "__main__":
    train_species_model(num_epochs=3, batch_size=32)
