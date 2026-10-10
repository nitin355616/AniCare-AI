import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
import numpy as np

try:
    from ai.inference.base import BaseInferenceEngine
    from ai.inference.demo_engine import demo_inference_engine
    from ai.inference.model_scope import model_scope_registry
    from ai.config import ai_config
    from ai.preprocessing.image_preprocessor import image_preprocessor
    from ai.preprocessing.tiled_preprocessor import tiled_preprocessor
    from ai.postprocessing.risk_engine import clinical_risk_engine
    from ai.explainability.gradcam import gradcam_explainer
except ImportError:
    from backend.ai.inference.base import BaseInferenceEngine
    from backend.ai.inference.demo_engine import demo_inference_engine
    from backend.ai.inference.model_scope import model_scope_registry
    from backend.ai.config import ai_config
    from backend.ai.preprocessing.image_preprocessor import image_preprocessor
    from backend.ai.preprocessing.tiled_preprocessor import tiled_preprocessor
    from backend.ai.postprocessing.risk_engine import clinical_risk_engine
    from backend.ai.explainability.gradcam import gradcam_explainer

from app.schemas.detection import DetectionAnalyzeRequest, DifferentialDiagnosisItem

logger = logging.getLogger("anicare.vision_engine")


class RealVisionInferenceEngine(BaseInferenceEngine):
    """
    Production livestock computer-vision inference engine running on ONNX Runtime.
    Processes bovine images using calibrated deep neural networks (EfficientNet-B0)
    with Platt temperature scaling, multi-modal risk stratification,
    species validation guardrails, and optional Grad-CAM explainability.

    SAFETY & RESILIENCE:
    If trained model weights are absent on disk, image is absent, or species is unvalidated,
    this engine safely falls back to DemoInferenceEngine baseline, ensuring
    continuous system uptime and uncompromised API availability.
    """

    def __init__(
        self,
        onnx_weights_path: Path = ai_config.DEFAULT_ONNX_PATH,
        torch_weights_path: Path = ai_config.DEFAULT_TORCH_PATH,
        device: str = ai_config.EXECUTION_DEVICE
    ):
        self.onnx_weights_path = onnx_weights_path
        self.torch_weights_path = torch_weights_path
        self.device = device
        self._session = None
        self.optimal_temperature: float = 1.4415
        self.operating_threshold: float = ai_config.OPERATING_THRESHOLD
        self.class_names: List[str] = ["Healthy / Normal", "Lumpy Skin Disease"]
        self.model_version: str = ai_config.MODEL_VERSION
        self.architecture: str = ai_config.MODEL_ARCHITECTURE

        self._load_metadata()

    def _load_metadata(self) -> None:
        """Loads optimal temperature and model parameters from metadata json if available."""
        meta_path = self.onnx_weights_path.with_suffix(".json")
        if meta_path.is_file():
            try:
                with open(meta_path, "r", encoding="utf-8") as f:
                    meta = json.load(f)
                    self.optimal_temperature = float(meta.get("optimal_temperature", 1.4415))
                    self.class_names = meta.get("class_names", self.class_names)
                    self.architecture = meta.get("architecture", self.architecture)
                    self.model_version = f"AniCare-Bovine-Vision v1.0-ONNX ({self.architecture})"
            except Exception as e:
                logger.warning(f"Could not load vision model metadata: {e}")

        # Check threshold analysis
        thresh_path = self.onnx_weights_path.parent.parent / "evaluation" / "threshold_analysis.json"
        if thresh_path.is_file():
            try:
                with open(thresh_path, "r", encoding="utf-8") as f:
                    tdata = json.load(f)
                    self.operating_threshold = float(tdata.get("selected_operating_threshold", 0.50))
            except Exception:
                self.operating_threshold = 0.50

    def has_weights(self) -> bool:
        """Checks if physical model weights file is deployed on disk."""
        return self.onnx_weights_path.is_file() or self.torch_weights_path.is_file()

    def has_runtime(self) -> bool:
        """Checks if ONNX Runtime or PyTorch runtime packages are importable."""
        try:
            import onnxruntime  # noqa: F401
            return True
        except ImportError:
            pass

        try:
            import torch  # noqa: F401
            return True
        except ImportError:
            pass

        return False

    def is_available(self) -> bool:
        """Vision engine is active only if weights file exists AND runtime is installed."""
        return self.has_weights() and self.has_runtime()

    def _get_session(self):
        """Lazy loader for ONNX Runtime session."""
        if self._session is None and self.onnx_weights_path.is_file():
            try:
                import onnxruntime as ort
                opts = ort.SessionOptions()
                opts.intra_op_num_threads = 2
                opts.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
                self._session = ort.InferenceSession(
                    str(self.onnx_weights_path),
                    sess_options=opts,
                    providers=["CPUExecutionProvider"]
                )
            except Exception as e:
                logger.error(f"Failed to initialize ONNX Runtime session: {e}")
                self._session = None
        return self._session

    def get_model_metadata(self) -> Dict[str, Any]:
        return {
            "engine": "RealVisionInferenceEngine",
            "model_version": self.model_version,
            "architecture": self.architecture,
            "device": self.device,
            "weights_present": self.has_weights(),
            "runtime_available": self.has_runtime(),
            "is_demo_inference": not self.is_available(),
            "status": "operational" if self.is_available() else "weights_pending_fallback_active",
            "optimal_temperature": self.optimal_temperature,
            "operating_threshold": self.operating_threshold,
            "model_scope": model_scope_registry.get_full_architecture_roadmap()
        }

    async def infer(
        self,
        data: DetectionAnalyzeRequest,
        image_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes vision assessment on animal photograph with multi-modal risk scoring.
        Enforces species validation guard and graceful fallback.
        """
        # 1. Species Validation Guard
        is_species_val, scope_def = model_scope_registry.resolve_species_scope(data.species)
        if not is_species_val:
            logger.info(
                f"Species '{data.species}' not validated for bovine vision model. "
                "Routing safely to syndromic assessment + veterinary review."
            )
            demo_res = await demo_inference_engine.infer(data, image_path=image_path)
            demo_res["model_scope"] = scope_def.model_dump()
            demo_res["disclaimer"] = (
                f"SPECIES NOTICE: Vision model validated exclusively for Cattle (Bovine). "
                f"Assessment for '{data.species}' conducted via syndromic symptoms only. "
                "This early-warning assist tool does not issue medical prescriptions or provide "
                "a confirmed medical diagnosis without on-site examination by a licensed veterinary officer."
            )
            return demo_res

        # 2. Fallback guard if weights or runtime are unavailable
        if not self.is_available():
            logger.info(
                "RealVisionInferenceEngine weights not deployed or runtime pending. "
                "Safely delegating inference to DemoInferenceEngine fallback."
            )
            demo_res = await demo_inference_engine.infer(data, image_path=image_path)
            demo_res["model_scope"] = scope_def.model_dump()
            return demo_res

        # 3. Fallback guard if no image was provided with request
        if not image_path or not os.path.isfile(image_path):
            logger.info("No valid image path provided for RealVisionInferenceEngine. Delegating to Demo engine.")
            demo_res = await demo_inference_engine.infer(data, image_path=image_path)
            demo_res["model_scope"] = scope_def.model_dump()
            return demo_res

        try:
            session = self._get_session()
            if session is None:
                logger.warning("ONNX session not initialized. Falling back to Demo engine.")
                demo_res = await demo_inference_engine.infer(data, image_path=image_path)
                demo_res["model_scope"] = scope_def.model_dump()
                return demo_res

            input_name = session.get_inputs()[0].name
            temp = max(0.1, self.optimal_temperature)

            # 4. Multi-Crop Tiled Inference vs Standard 224x224
            if getattr(data, "enable_tiled_inference", False):
                crops, meta = tiled_preprocessor.extract_crops(image_path)
                crop_lsd_probs: List[float] = []
                for c_tensor in crops:
                    raw_logits = session.run(None, {input_name: c_tensor})[0]
                    scaled_logits = raw_logits / temp
                    e_logits = np.exp(scaled_logits - np.max(scaled_logits, axis=-1, keepdims=True))
                    probs = e_logits / np.sum(e_logits, axis=-1, keepdims=True)
                    crop_lsd_probs.append(float(probs[0, 1]))

                agg_res = tiled_preprocessor.aggregate_crop_predictions(crop_lsd_probs)
                prob_lsd = agg_res["final_prob"]
                prob_healthy = round(1.0 - prob_lsd, 4)
            else:
                tensor, meta = image_preprocessor.preprocess(image_path)
                raw_logits = session.run(None, {input_name: tensor})[0]  # Shape [1, 2]
                scaled_logits = raw_logits / temp
                exp_logits = np.exp(scaled_logits - np.max(scaled_logits, axis=-1, keepdims=True))
                probs = exp_logits / np.sum(exp_logits, axis=-1, keepdims=True)
                prob_healthy = float(probs[0, 0])
                prob_lsd = float(probs[0, 1])

            # 5. Operating Decision Threshold
            threshold = self.operating_threshold
            is_lsd_flagged = prob_lsd >= threshold

            # 6. Map Visual Predictions & Differentials
            if is_lsd_flagged:
                possible_condition = "Lumpy Skin Disease (Capripox - Visual Presentation)"
                confidence = round(prob_lsd * 100.0, 1)
                visual_indicators = [
                    "Circumscribed dermal nodules (2-5cm diameter)",
                    "Elevated epidermal lesion clusters",
                    "Cutaneous focal inflammation"
                ]
                explanation = (
                    f"Deep vision classifier detected cutaneous nodular patterns consistent with "
                    f"Capripoxvirus (Lumpy Skin Disease) with calibrated visual confidence of {confidence}%. "
                    f"Biosecurity isolation and insect-vector containment are advised."
                )
                immediate_actions = [
                    "Immediate physical isolation of affected animal under vector-proof mesh netting.",
                    "Notify local District Veterinary Officer (DVO) for regulatory sampling.",
                    "Apply topical antiseptic sprays to prevent secondary bacterial infection on ruptured nodules.",
                    "Daily photographic tracking of nodular lesion spread."
                ]
                preventive_actions = [
                    "Institute ring vaccination with homologous Goat Pox vaccine (10x cattle dose).",
                    "Thermal vector fogging (deltamethrin or neem-based formulations) across shed.",
                    "Eliminate stagnant water breeding pools around dairy pens."
                ]
                differentials = [
                    DifferentialDiagnosisItem(
                        disease="Lumpy Skin Disease",
                        probability=confidence,
                        rationale="Circumscribed dermal nodules with epidermal elevation."
                    ),
                    DifferentialDiagnosisItem(
                        disease="Pseudo-Lumpy Skin Disease (BHV-2)",
                        probability=round(min(prob_healthy * 60.0, 15.0), 1),
                        rationale="Superficial crusts without deep cutaneous necrosis."
                    ),
                    DifferentialDiagnosisItem(
                        disease="Healthy / Normal Bovine",
                        probability=round(prob_healthy * 100.0, 1),
                        rationale="Residual baseline probability from visual classifier."
                    )
                ]
                symptoms_detected = [
                    "Circumscribed cutaneous nodules",
                    "Dermal papular lesions",
                    "Localized epidermal swelling"
                ]
            else:
                possible_condition = "Healthy / Normal Bovine (No Cutaneous Lesions Detected)"
                confidence = round(prob_healthy * 100.0, 1)
                visual_indicators = [
                    "Clean epidermal contour",
                    "Uniform hair coat texture",
                    "Absence of circumscribed dermal nodules"
                ]
                explanation = (
                    f"Deep vision classifier found no visual evidence of cutaneous nodules or "
                    f"Capripoxvirus lesions (Calibrated healthy confidence: {confidence}%)."
                )
                immediate_actions = [
                    "Continue routine daily herd health observation.",
                    "Maintain standard shed sanitation and vector control measures.",
                    "Record normal baseline vitals in herd log."
                ]
                preventive_actions = [
                    "Adhere to routine annual preventative vaccination schedule.",
                    "Ensure adequate clean drinking water and balanced nutrition.",
                    "Maintain biosecure boundary fencing against roaming livestock."
                ]
                differentials = [
                    DifferentialDiagnosisItem(
                        disease="Healthy / Normal Bovine",
                        probability=confidence,
                        rationale="Absence of cutaneous lesions or nodular skin eruptions."
                    ),
                    DifferentialDiagnosisItem(
                        disease="Subclinical Incubation / Early Phase",
                        probability=round(prob_lsd * 100.0, 1),
                        rationale="Early pre-eruptive viremic phase cannot be ruled out by visual scan alone."
                    )
                ]
                symptoms_detected = [
                    "No visible cutaneous lesions"
                ]

            # 7. Multi-Modal Clinical Risk Stratification
            risk_eval = clinical_risk_engine.evaluate_risk(
                condition_name="Lumpy Skin Disease" if is_lsd_flagged else "Healthy / Normal",
                confidence=confidence,
                species=data.species or "Cattle",
                symptoms=data.symptoms,
                temperature=data.temperature,
                appetite=data.appetite,
                activity_level=data.activity_level,
                breathing_condition=data.breathing_condition,
                observations=data.observations,
                heart_rate=getattr(data, "heart_rate", None),
                respiratory_rate=getattr(data, "respiratory_rate", None),
                vaccination_status=getattr(data, "vaccination_status", "UNKNOWN"),
                age_months=getattr(data, "age_months", None),
                recent_nearby_cases=getattr(data, "recent_nearby_cases", 0),
                herd_at_risk_count=getattr(data, "herd_at_risk_count", 0),
                cluster_warning_active=getattr(data, "cluster_warning_active", False),
                recent_movement=getattr(data, "recent_movement", False),
                image_quality="ADEQUATE"
            )

            # Match symptoms provided in request
            evidence_symptoms = [
                s for s in data.symptoms
                if any(w in s.lower() for w in ["nodule", "skin", "lump", "fever", "lesion", "swell"])
            ]

            # 8. Optional Grad-CAM Visual Explainability
            explainability_meta = None
            if getattr(data, "request_explainability", False):
                explainability_meta = gradcam_explainer.generate_heatmap(
                    image_path=image_path,
                    target_class_idx=1 if is_lsd_flagged else 0,
                    image_id=data.image_id
                )

            return {
                # Core existing fields
                "possible_condition": possible_condition,
                "confidence": confidence,
                "risk_level": risk_eval["risk_level"],
                "risk_score": risk_eval["risk_score"],
                "risk_reasoning": risk_eval["risk_reasoning"],
                "contributing_factors": risk_eval["contributing_factors"],
                "symptoms_detected": symptoms_detected,
                "symptom_evidence": evidence_symptoms,
                "detected_visual_indicators": visual_indicators,
                "explanation": explanation,
                "recommended_immediate_actions": immediate_actions,
                "veterinary_review_required": True,
                "preventive_actions": preventive_actions,
                "differential_diagnoses": differentials,
                "is_demo_inference": False,
                "model_version": self.model_version,
                # Milestone 6 Multi-Modal extensions
                "visual_risk_score": risk_eval["visual_risk_score"],
                "symptom_risk_score": risk_eval["symptom_risk_score"],
                "physiological_risk_score": risk_eval["physiological_risk_score"],
                "epidemiological_risk_score": risk_eval["epidemiological_risk_score"],
                "history_risk_score": risk_eval["history_risk_score"],
                "overall_risk_score": risk_eval["overall_risk_score"],
                "model_scope": scope_def.model_dump(),
                "operating_threshold": threshold,
                "explainability": explainability_meta
            }

        except Exception as exc:
            logger.error(
                f"Exception during RealVisionInferenceEngine execution: {exc}. "
                "Safely falling back to DemoInferenceEngine.",
                exc_info=True
            )
            demo_res = await demo_inference_engine.infer(data, image_path=image_path)
            demo_res["model_scope"] = scope_def.model_dump()
            return demo_res


vision_inference_engine = RealVisionInferenceEngine()


def get_inference_engine(prefer_vision: bool = True) -> BaseInferenceEngine:
    """
    Factory selector: Returns RealVisionInferenceEngine if operational,
    otherwise returns DemoInferenceEngine as safe fallback.
    """
    if prefer_vision and vision_inference_engine.is_available():
        return vision_inference_engine
    return demo_inference_engine
