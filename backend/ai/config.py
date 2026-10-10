import os
from pathlib import Path
from typing import List, Tuple

class AIConfig:
    """
    Configuration specifications for AniCare AI model deployment,
    edge inference, image preprocessing pipelines, and risk stratification.
    """
    # Architecture and framework
    FRAMEWORK_TARGET: str = "onnx"  # Target inference runtime: 'onnx' | 'pytorch'
    MODEL_ARCHITECTURE: str = "EfficientNet-B0"  # Compound scaled deep vision model
    MODEL_VERSION: str = "AniCare-Bovine-Vision v1.0-ONNX"
    DEMO_MODEL_VERSION: str = "AniCare-Net v1.2-DemoEngine"

    # Execution hardware
    EXECUTION_DEVICE: str = "cpu"  # Default to CPU; switches to 'cuda' when available
    ALLOW_GPU: bool = True
    MAX_BATCH_SIZE: int = 1
    INFERENCE_TIMEOUT_SECONDS: float = 5.0

    # Weights paths
    AI_BASE_DIR: Path = Path(__file__).resolve().parent
    WEIGHTS_DIR: Path = AI_BASE_DIR / "models" / "weights"
    DEFAULT_ONNX_PATH: Path = WEIGHTS_DIR / "anicare_vision_bovine_v1.onnx"
    DEFAULT_TORCH_PATH: Path = WEIGHTS_DIR / "anicare_vision_bovine_v1.pt"

    # Image preprocessing parameters
    IMAGE_INPUT_SIZE: Tuple[int, int] = (224, 224)
    NORM_MEAN: Tuple[float, float, float] = (0.485, 0.456, 0.406)
    NORM_STD: Tuple[float, float, float] = (0.229, 0.224, 0.225)
    ALLOWED_IMAGE_FORMATS: Tuple[str, ...] = ("image/jpeg", "image/png", "image/webp")
    MAX_IMAGE_FILE_SIZE_MB: int = 10

    # Decision thresholds
    CONFIDENCE_THRESHOLD_MIN: float = 0.50
    CONFIDENCE_THRESHOLD_HIGH: float = 0.85

    # Frozen Operating Threshold (Selected on Validation Set only; test set diagnostics NOT used for selection)
    OPERATING_THRESHOLD: float = 0.50
    OPERATING_THRESHOLD_FROZEN: bool = True
    OPERATING_THRESHOLD_SELECTION_SOURCE: str = "validation_set_only"
    OPERATING_THRESHOLD_SELECTION_RULE: str = "maximize recall subject to specificity >= 90% on validation"

    # Target classes under OIE & ICAR veterinary taxonomy
    TARGET_CLASSES: List[str] = [
        "Foot and Mouth Disease",
        "Lumpy Skin Disease",
        "Respiratory Infection",
        "Bovine Mastitis",
        "Healthy / Normal"
    ]

    TARGET_SPECIES: List[str] = [
        "Cattle",
        "Buffalo",
        "Goat",
        "Sheep"
    ]

    # Precautionary safety fallback
    FALLBACK_TO_DEMO_ENABLED: bool = True

ai_config = AIConfig()
