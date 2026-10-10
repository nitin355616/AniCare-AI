import abc
from typing import Dict, Any, Optional, List
from app.schemas.detection import DetectionAnalyzeRequest

class BaseInferenceEngine(abc.ABC):
    """
    Abstract Base Class establishing the contract for all AniCare AI inference engines.
    Ensures seamless drop-in substitution between rule-based simulation engines
    and future trained PyTorch / ONNX deep learning vision backends.
    """

    @abc.abstractmethod
    async def infer(
        self,
        data: DetectionAnalyzeRequest,
        image_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes disease assessment.
        Must return a structured dictionary conforming to the API contract.
        """
        pass

    @abc.abstractmethod
    def is_available(self) -> bool:
        """
        Returns True if the engine's dependencies, runtime libraries,
        and model weights are fully loaded and operational.
        """
        pass

    @abc.abstractmethod
    def get_model_metadata(self) -> Dict[str, Any]:
        """
        Returns model version, architecture, execution device, and safety parameters.
        """
        pass
