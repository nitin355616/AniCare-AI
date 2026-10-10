"""
AniCare AI — Vision Model Training Package
"""

try:
    from .config import TrainingConfig
    from .transforms import get_train_transforms, get_eval_transforms
    from .dataset import BovineDiseaseDataset, create_dataloaders
    from .losses import FocalLoss, create_criterion
    from .model import BovineVisionClassifier, build_model
    from .metrics import compute_metrics
    from .calibration import compute_ece, ModelTemperatureScaler
    from .evaluate import evaluate_dataloader
    from .train import train_model
    from .utils import set_seed, plot_and_save_confusion_matrix, export_model_to_onnx, verify_onnx_parity

    __all__ = [
        "TrainingConfig",
        "get_train_transforms",
        "get_eval_transforms",
        "BovineDiseaseDataset",
        "create_dataloaders",
        "FocalLoss",
        "create_criterion",
        "BovineVisionClassifier",
        "build_model",
        "compute_metrics",
        "compute_ece",
        "ModelTemperatureScaler",
        "evaluate_dataloader",
        "train_model",
        "set_seed",
        "plot_and_save_confusion_matrix",
        "export_model_to_onnx",
        "verify_onnx_parity",
    ]
except (ImportError, ModuleNotFoundError):
    __all__ = []
