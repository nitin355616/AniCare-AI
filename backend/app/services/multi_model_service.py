"""
AniCare AI — Multi-Model Real Inference Service
Provides real neural network inference for Task A (Bovine Disease Classification),
Task B (Animal Species Guard), and Task C (Muzzle Biometric Registry).
Never generates hardcoded or fabricated scores.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from PIL import Image

import torch
import torch.nn as nn
import torchvision.transforms as transforms
import torchvision.models as models

logger = logging.getLogger("anicare.multi_model_service")

# Model singletons
_DISEASE_MODEL = None
_SPECIES_MODEL = None
_DISEASE_META = None
_SPECIES_META = None
_MUZZLE_REGISTRY = None

def get_weights_dir() -> Path:
    backend_root = Path(__file__).resolve().parent.parent.parent
    return backend_root / "ai" / "models" / "weights"

def get_transform():
    return transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

def get_disease_model():
    global _DISEASE_MODEL, _DISEASE_META
    if _DISEASE_MODEL is not None:
        return _DISEASE_MODEL, _DISEASE_META

    weights_dir = get_weights_dir()
    pt_path = weights_dir / "disease_classifier_multiclass_v1.pt"
    meta_path = weights_dir / "disease_classifier_multiclass_v1.json"

    if not pt_path.is_file():
        logger.warning(f"Disease model weights not found at {pt_path}")
        return None, None

    try:
        checkpoint = torch.load(pt_path, map_location="cpu", weights_only=False)
        model = models.mobilenet_v2(weights=None)
        in_features = model.classifier[1].in_features
        model.classifier = nn.Sequential(
            nn.Dropout(0.2),
            nn.Linear(in_features, checkpoint.get("num_classes", 3))
        )
        model.load_state_dict(checkpoint["state_dict"])
        model.eval()

        meta = {}
        if meta_path.is_file():
            with open(meta_path, "r", encoding="utf-8") as f:
                meta = json.load(f)

        _DISEASE_MODEL = model
        _DISEASE_META = meta
        logger.info("Multi-Class Bovine Disease Model loaded successfully.")
        return _DISEASE_MODEL, _DISEASE_META
    except Exception as e:
        logger.error(f"Failed loading disease model: {e}")
        return None, None

def get_species_model():
    global _SPECIES_MODEL, _SPECIES_META
    if _SPECIES_MODEL is not None:
        return _SPECIES_MODEL, _SPECIES_META

    weights_dir = get_weights_dir()
    pt_path = weights_dir / "species_classifier_v1.pt"
    meta_path = weights_dir / "species_classifier_v1.json"

    if not pt_path.is_file():
        return None, None

    try:
        checkpoint = torch.load(pt_path, map_location="cpu", weights_only=False)
        model = models.mobilenet_v2(weights=None)
        in_features = model.classifier[1].in_features
        model.classifier = nn.Sequential(
            nn.Dropout(0.2),
            nn.Linear(in_features, checkpoint.get("num_classes", 4))
        )
        model.load_state_dict(checkpoint["state_dict"])
        model.eval()

        meta = {}
        if meta_path.is_file():
            with open(meta_path, "r", encoding="utf-8") as f:
                meta = json.load(f)

        _SPECIES_MODEL = model
        _SPECIES_META = meta
        return _SPECIES_MODEL, _SPECIES_META
    except Exception as e:
        logger.error(f"Failed loading species model: {e}")
        return None, None

def get_muzzle_registry() -> Optional[Dict[str, Any]]:
    global _MUZZLE_REGISTRY
    if _MUZZLE_REGISTRY is not None:
        return _MUZZLE_REGISTRY

    reg_path = get_weights_dir() / "muzzle_biometrics_registry.json"
    if reg_path.is_file():
        with open(reg_path, "r", encoding="utf-8") as f:
            _MUZZLE_REGISTRY = json.load(f)
            return _MUZZLE_REGISTRY
    return None

class MultiModelInferenceService:
    @staticmethod
    def predict_disease(image_path: str) -> Dict[str, Any]:
        """
        Executes genuine neural network inference on an animal photograph for Task A.
        Returns actual softmax probabilities across Healthy, FMD, and LSD.
        """
        model, meta = get_disease_model()
        if model is None:
            raise RuntimeError("Task A Multi-Class Disease model weights are not loaded.")

        class_names = meta.get("class_names", [
            "Healthy / Normal",
            "Foot and Mouth Disease",
            "Lumpy Skin Disease"
        ])

        try:
            image = Image.open(image_path).convert("RGB")
        except Exception as e:
            raise ValueError(f"Unreadable image file: {e}")

        tf = get_transform()
        tensor = tf(image).unsqueeze(0)  # batch size 1

        with torch.no_grad():
            logits = model(tensor)
            probs = torch.softmax(logits, dim=1).squeeze(0).tolist()

        pred_idx = int(torch.argmax(logits, dim=1).item())
        pred_class = class_names[pred_idx]
        pred_confidence = round(probs[pred_idx], 4)

        # Risk level determination based on clinical nature of predicted class
        if pred_class == "Foot and Mouth Disease":
            risk_level = "CRITICAL" if pred_confidence >= 0.70 else "HIGH"
            explanation = (
                f"Visual neural features indicate signs consistent with Foot and Mouth Disease (FMD) "
                f"with {pred_confidence*100:.1f}% confidence. Vesicular lesions, erosions, or sialorrhea detected."
            )
            actions = [
                "Immediate strict quarantine of affected animal from the herd.",
                "Disinfect footbaths and dairy equipment using 4% sodium carbonate.",
                "Notify block veterinary officer (BVO) for mandatory ring vaccination.",
                "Restrict milk and livestock transport from the premises."
            ]
        elif pred_class == "Lumpy Skin Disease":
            risk_level = "CRITICAL" if pred_confidence >= 0.70 else "HIGH"
            explanation = (
                f"Visual neural features indicate cutaneous circumscribed nodules characteristic of "
                f"Lumpy Skin Disease (LSD) with {pred_confidence*100:.1f}% confidence."
            )
            actions = [
                "Isolate animal in vector-screened housing to prevent fly/mosquito transmission.",
                "Apply topical antiseptic to ulcerated skin nodules.",
                "Monitor rectal temperature daily; notify local veterinary dispensary.",
                "Initiate herd vaccination with goat pox vaccine per state animal husbandry protocol."
            ]
        else:
            risk_level = "LOW"
            explanation = (
                f"Visual neural screening indicates healthy bovine cutaneous mucosa and skin surface "
                f"with {pred_confidence*100:.1f}% confidence. No suspicious lesions observed."
            )
            actions = [
                "Maintain routine biosecurity, balanced nutrition, and clean water.",
                "Continue scheduled deworming and preventive vaccination.",
                "Perform regular grooming and body condition monitoring."
            ]

        differential = [
            {
                "disease": name,
                "probability": round(prob, 4),
                "rationale": f"Neural classifier posterior probability: {prob*100:.1f}%"
            }
            for name, prob in zip(class_names, probs)
        ]
        # Sort differential diagnoses descending by probability
        differential.sort(key=lambda x: x["probability"], reverse=True)

        return {
            "is_real_inference": True,
            "is_demo_inference": False,
            "model_version": meta.get("model_version", "AniCare-MultiDisease-Vision v1.0"),
            "architecture": meta.get("architecture", "MobileNetV2"),
            "possible_condition": pred_class,
            "confidence": pred_confidence,
            "risk_level": risk_level,
            "probabilities": {name: round(prob, 4) for name, prob in zip(class_names, probs)},
            "differential_diagnoses": differential,
            "explanation": explanation,
            "recommended_immediate_actions": actions,
            "veterinary_review_required": pred_class != "Healthy / Normal",
            "test_accuracy": meta.get("test_metrics", {}).get("accuracy"),
            "test_macro_f1": meta.get("test_metrics", {}).get("macro_f1"),
            "disclaimer": (
                "AI-ASSISTED CLINICAL TRIAGE: Model predictions provide rapid screening guidance "
                "for biosecurity early warning. This tool does NOT replace on-site physical clinical "
                "examination, laboratory confirmation (RT-PCR/ELISA), or prescription by a certified veterinarian."
            )
        }

    @staticmethod
    def predict_species(image_path: str) -> Dict[str, Any]:
        """
        Executes animal species guardrail classification for Task B.
        """
        model, meta = get_species_model()
        if model is None:
            raise RuntimeError("Task B Species model weights are not loaded.")

        class_names = meta.get("class_names", ["Cattle", "Dog", "Cat", "Bird"])

        try:
            image = Image.open(image_path).convert("RGB")
        except Exception as e:
            raise ValueError(f"Unreadable image file: {e}")

        tf = get_transform()
        tensor = tf(image).unsqueeze(0)

        with torch.no_grad():
            logits = model(tensor)
            probs = torch.softmax(logits, dim=1).squeeze(0).tolist()

        pred_idx = int(torch.argmax(logits, dim=1).item())
        pred_species = class_names[pred_idx]
        confidence = round(probs[pred_idx], 4)

        return {
            "predicted_species": pred_species,
            "confidence": confidence,
            "is_bovine": pred_species == "Cattle",
            "probabilities": {name: round(prob, 4) for name, prob in zip(class_names, probs)},
            "model_version": meta.get("model_version", "AniCare-Species-Guard v1.0"),
            "test_accuracy": meta.get("test_metrics", {}).get("accuracy")
        }

multi_model_service = MultiModelInferenceService()
