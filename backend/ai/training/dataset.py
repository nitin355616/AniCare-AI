"""
AniCare AI — PyTorch Dataset & DataLoader Factory
Loads images directly from verified manifest records with split isolation.
"""

import os
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Any
from PIL import Image
import torch
from torch.utils.data import Dataset, DataLoader

try:
    from ai.dataset.schema import DatasetManifestRecord, DatasetSplitEnum
    from ai.dataset.manifest import DatasetManifestManager
    from ai.training.config import TrainingConfig
    from ai.training.transforms import get_train_transforms, get_eval_transforms
except ImportError:
    from backend.ai.dataset.schema import DatasetManifestRecord, DatasetSplitEnum
    from backend.ai.dataset.manifest import DatasetManifestManager
    from backend.ai.training.config import TrainingConfig
    from backend.ai.training.transforms import get_train_transforms, get_eval_transforms


class BovineDiseaseDataset(Dataset):
    """PyTorch Dataset loading images using canonical DatasetManifestRecord specifications."""

    def __init__(
        self,
        records: List[DatasetManifestRecord],
        backend_root: Path,
        transform=None,
        class_to_idx: Optional[Dict[str, int]] = None
    ):
        self.records = records
        self.backend_root = Path(backend_root)
        self.transform = transform
        self.class_to_idx = class_to_idx or {
            "Healthy / Normal": 0,
            "Lumpy Skin Disease": 1
        }

    def __len__(self) -> int:
        return len(self.records)

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, int, str, str]:
        rec = self.records[idx]
        image_path = self.backend_root / rec.file_path

        if not image_path.exists():
            raise FileNotFoundError(f"Dataset image missing on disk: {image_path}")

        with Image.open(image_path) as img:
            img = img.convert("RGB")
            if self.transform:
                tensor = self.transform(img)
            else:
                tensor = transforms.ToTensor()(img)

        label_idx = self.class_to_idx[rec.disease]
        return tensor, label_idx, rec.image_id, rec.file_path


def create_dataloaders(config: TrainingConfig) -> Tuple[DataLoader, DataLoader, DataLoader, Dict[str, Any]]:
    """
    Constructs isolated Train, Validation, and Test DataLoaders from processed manifest.json.
    Computes class frequency weights to handle biological class imbalance.
    """
    records = DatasetManifestManager.load_from_json(str(config.manifest_path))

    train_records = [r for r in records if r.split == DatasetSplitEnum.TRAIN]
    val_records = [r for r in records if r.split == DatasetSplitEnum.VALIDATION]
    test_records = [r for r in records if r.split == DatasetSplitEnum.TEST]

    print(f"DataLoaders partition count:")
    print(f" - Train:      {len(train_records)} images")
    print(f" - Validation: {len(val_records)} images")
    print(f" - Test:       {len(test_records)} images (Held out strictly)")

    # Compute class distribution in training partition
    train_labels = [config.class_to_idx[r.disease] for r in train_records]
    class_counts = [
        train_labels.count(0),  # Healthy / Normal
        train_labels.count(1),  # Lumpy Skin Disease
    ]
    total_train = len(train_labels)

    # Inverse class frequency weights for standard cross-entropy: total / (num_classes * count)
    class_weights = [
        total_train / (config.num_classes * max(class_counts[0], 1)),
        total_train / (config.num_classes * max(class_counts[1], 1))
    ]

    # Normalized alpha weights for Focal Loss
    sum_weights = sum(class_weights)
    focal_alpha = [w / sum_weights for w in class_weights]

    train_dataset = BovineDiseaseDataset(
        train_records,
        config.backend_root,
        transform=get_train_transforms(config.image_size),
        class_to_idx=config.class_to_idx
    )
    val_dataset = BovineDiseaseDataset(
        val_records,
        config.backend_root,
        transform=get_eval_transforms(config.image_size),
        class_to_idx=config.class_to_idx
    )
    test_dataset = BovineDiseaseDataset(
        test_records,
        config.backend_root,
        transform=get_eval_transforms(config.image_size),
        class_to_idx=config.class_to_idx
    )

    train_loader = DataLoader(
        train_dataset,
        batch_size=config.batch_size,
        shuffle=True,
        num_workers=config.num_workers,
        pin_memory=False
    )
    val_loader = DataLoader(
        val_dataset,
        batch_size=config.batch_size,
        shuffle=False,
        num_workers=config.num_workers,
        pin_memory=False
    )
    test_loader = DataLoader(
        test_dataset,
        batch_size=config.batch_size,
        shuffle=False,
        num_workers=config.num_workers,
        pin_memory=False
    )

    meta = {
        "train_class_counts": class_counts,
        "class_weights": class_weights,
        "focal_alpha": focal_alpha,
        "train_size": len(train_records),
        "val_size": len(val_records),
        "test_size": len(test_records)
    }

    return train_loader, val_loader, test_loader, meta
