"""
AniCare AI — Vision Model Training Configuration
Centralized configuration parameters, reproducibility seeds, and hyperparameters.
"""

import os
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from pathlib import Path


@dataclass
class TrainingConfig:
    """Hyperparameters and runtime configuration for bovine vision model training."""
    
    # Reproducibility
    seed: int = 42
    
    # Dataset and labels
    # Index 0: Healthy / Normal, Index 1: Lumpy Skin Disease
    class_names: List[str] = field(default_factory=lambda: ["Healthy / Normal", "Lumpy Skin Disease"])
    class_to_idx: Dict[str, int] = field(default_factory=lambda: {
        "Healthy / Normal": 0,
        "Lumpy Skin Disease": 1
    })
    num_classes: int = 2
    
    # Image preprocessing
    image_size: int = 224
    imagenet_mean: List[float] = field(default_factory=lambda: [0.485, 0.456, 0.406])
    imagenet_std: List[float] = field(default_factory=lambda: [0.229, 0.224, 0.225])
    
    # Hardware & DataLoader
    batch_size: int = 16
    num_workers: int = 0  # 0 on Windows to avoid multi-process spawn overhead
    device: str = "cpu"
    
    # Two-Phase Transfer Learning Strategy
    # Phase 1: Backbone frozen, train linear classifier head
    phase1_epochs: int = 5
    phase1_lr: float = 1e-3
    
    # Phase 2: Unfreeze upper backbone blocks for fine-tuning
    phase2_epochs: int = 8
    phase2_lr: float = 1e-4
    
    weight_decay: float = 1e-4
    early_stopping_patience: int = 4
    
    # Loss configuration: "focal" or "weighted_ce"
    loss_type: str = "focal"
    focal_gamma: float = 2.0
    focal_alpha: Optional[List[float]] = None  # Computed dynamically from class distribution
    
    # Target Metric Thresholds (Targets only — never manipulated)
    target_lsd_recall: float = 0.92
    target_macro_f1: float = 0.85
    target_ece: float = 0.08
    
    # File Paths
    backend_root: Path = field(default_factory=lambda: Path(r"d:\AniCare-AI\backend"))
    manifest_path: Path = field(default_factory=lambda: Path(r"d:\AniCare-AI\backend\ai\dataset\processed\manifest.json"))
    checkpoints_dir: Path = field(default_factory=lambda: Path(r"d:\AniCare-AI\backend\ai\models\checkpoints"))
    evaluation_dir: Path = field(default_factory=lambda: Path(r"d:\AniCare-AI\backend\ai\models\evaluation"))
    weights_dir: Path = field(default_factory=lambda: Path(r"d:\AniCare-AI\backend\ai\models\weights"))
