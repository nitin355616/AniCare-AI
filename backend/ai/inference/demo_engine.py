from typing import Dict, Any, Optional, List

try:
    from ai.inference.base import BaseInferenceEngine
    from ai.config import ai_config
    from ai.postprocessing.risk_engine import clinical_risk_engine
except ImportError:
    from backend.ai.inference.base import BaseInferenceEngine
    from backend.ai.config import ai_config
    from backend.ai.postprocessing.risk_engine import clinical_risk_engine

from app.schemas.detection import DetectionAnalyzeRequest, DifferentialDiagnosisItem

class DemoInferenceEngine(BaseInferenceEngine):
    """
    Simulation inference engine explicitly designed for SIH 2026 prototyping.
    Evaluates multivariable symptom profiles and telemetry thresholds to provide
    clinically plausible differential evaluations under OIE and ICAR taxonomy.
    """

    def is_available(self) -> bool:
        """Demo engine has zero external dependencies and is always available."""
        return True

    def get_model_metadata(self) -> Dict[str, Any]:
        return {
            "engine": "DemoInferenceEngine",
            "model_version": ai_config.DEMO_MODEL_VERSION,
            "architecture": "Heuristic Rule-Based Syndromic Knowledge Base",
            "device": "cpu",
            "is_demo_inference": True,
            "status": "operational"
        }

    async def infer(
        self,
        data: DetectionAnalyzeRequest,
        image_path: Optional[str] = None
    ) -> Dict[str, Any]:
        symptoms_str = " ".join(data.symptoms).lower()
        temp_val = clinical_risk_engine.parse_temperature(data.temperature) or 101.5

        # 1. Foot and Mouth Disease (FMD) signs
        if any(k in symptoms_str for k in ["salivation", "vesic", "mouth", "coronary", "tongue"]) or temp_val >= 104.7:
            possible_condition = "Foot and Mouth Disease (Suspected Vesicular Phase)"
            confidence = 94.6
            symptoms_detected = [
                "Hypersalivation (ropy drool pattern)",
                "Mouth mucosal vesicles and dental pad erosion",
                "Coronary band inflammation",
                f"Core pyrexia of {temp_val}°F"
            ]
            explanation = (
                "Syndromic triad of acute stomatitis, excessive salivation, and high fever strongly matches "
                "Aphthovirus epizootic presentation. High cohort transmission risk across the dairy shed."
            )
            immediate_actions = [
                "Immediate bio-secure isolation in quarantine pen (minimum 100m standoff).",
                "Notify District Animal Husbandry Officer (DAHO) under Infectious Diseases Act.",
                "Disinfect facility entryways with 4% sodium carbonate footbaths.",
                "Collect sterile vesicular fluid swab for RT-PCR confirmation at NIHSAD Bhopal."
            ]
            preventive_actions = [
                "Emergency ring vaccination of all susceptible livestock within 5km radius.",
                "Freeze animal movements and milk tanker dispatches from affected shed."
            ]
            differentials = [
                DifferentialDiagnosisItem(disease="Foot and Mouth Disease", probability=94.6, rationale="Vesicular erosion on oral mucosa and pododermatitis."),
                DifferentialDiagnosisItem(disease="Vesicular Stomatitis", probability=4.1, rationale="Similar oral ulcers but lower prevalence in this zone."),
                DifferentialDiagnosisItem(disease="Bovine Viral Diarrhea", probability=1.3, rationale="Absence of acute mucosal hemorrhagic enteritis.")
            ]
            visual_indicators = [
                "Ropy sialorrhea hanging from muzzle",
                "Ruptured vesicles on dental pad",
                "Coronary band hyperemia"
            ]

        # 2. Lumpy Skin Disease (LSD)
        elif any(k in symptoms_str for k in ["nodule", "skin", "lump", "lymph", "capripox"]):
            possible_condition = "Lumpy Skin Disease (Capripox)"
            confidence = 91.2
            symptoms_detected = [
                "Firm circumscribed 2-5cm cutaneous nodules",
                "Superficial lymphadenopathy",
                f"Elevated core temperature of {temp_val}°F",
                "Anorexia and localized limb edema"
            ]
            explanation = (
                "Discrete cutaneous nodules across neck and perineum correlate with Capripox viral replication. "
                "Vector transmission mediated by biting flies (Stomoxys) poses rapid herd-wide threat."
            )
            immediate_actions = [
                "Isolate animal under fine insect-proof mesh netting.",
                "Deploy thermal vector fogging (deltamethrin or neem-based formulations).",
                "Apply topical antiseptic sprays to prevent secondary bacterial infection on ruptured nodules.",
                "Daily photographic tracking of nodule regression."
            ]
            preventive_actions = [
                "Institute ring vaccination with homologous Goat Pox vaccine (10x cattle dose).",
                "Eliminate stagnant water breeding pools around dairy pens."
            ]
            differentials = [
                DifferentialDiagnosisItem(disease="Lumpy Skin Disease", probability=91.2, rationale="Circumscribed dermal nodules with lymph node enlargement."),
                DifferentialDiagnosisItem(disease="Pseudo-Lumpy Skin (BHV-2)", probability=6.7, rationale="Lesions deeper than typical herpesvirus superficial crusts."),
                DifferentialDiagnosisItem(disease="Demodectic Mange", probability=2.1, rationale="Rapid fever onset rules out slow parasitic mite infestation.")
            ]
            visual_indicators = [
                "Circumscribed dermal nodules (2-5cm diameter)",
                "Prescapular lymph node enlargement",
                "Brisk limb edema"
            ]

        # 3. Bovine Mastitis
        elif any(k in symptoms_str for k in ["mastitis", "udder", "milk", "conductivity", "quarter", "clot"]):
            possible_condition = "Subclinical / Acute Bovine Mastitis"
            confidence = 88.5
            symptoms_detected = [
                "Localized induration and heat in udder quarter",
                "Quarter milk electrical conductivity elevation",
                "Floccules observed in foremilk strip cup",
                "Daily milk yield depression"
            ]
            explanation = (
                "Telemetry indicators and localized mammary inflammation signify bacterial intraductal infection. "
                "Early intervention preserves quarter function and prevents permanent secretory tissue fibrosis."
            )
            immediate_actions = [
                "Milk out affected quarter completely into a separate discard container.",
                "Perform California Mastitis Test (CMT) strip verification.",
                "Aseptic milk sampling for microbiological culture and antimicrobial sensitivity (AST).",
                "Apply post-milking 0.5% active iodine barrier teat dip."
            ]
            preventive_actions = [
                "Inspect milking machine claw vacuum pulsator levels and liner integrity.",
                "Maintain clean, dry sand bedding dusted with calcium hydroxide."
            ]
            differentials = [
                DifferentialDiagnosisItem(disease="Subclinical / Clinical Mastitis", probability=88.5, rationale="Localized udder firmness and conductivity telemetry spike."),
                DifferentialDiagnosisItem(disease="Physiological Udder Edema", probability=8.9, rationale="Lactation period not in immediate periparturient phase."),
                DifferentialDiagnosisItem(disease="Traumatic Thelitis", probability=2.6, rationale="No mechanical laceration noted on teat sphincter.")
            ]
            visual_indicators = [
                "Quarter asymmetry and udder swelling",
                "Teat orifice hyperkeratosis"
            ]

        # 4. Bovine Respiratory Disease Complex
        else:
            possible_condition = "Respiratory Infection"
            confidence = 87.0
            symptoms_detected = [
                "Rapid, shallow dyspneic breathing",
                "Serous to mucopurulent bilateral nasal discharge",
                f"Core pyrexia of {temp_val}°F",
                "Depressed appetite and droopy ears"
            ]
            explanation = (
                "Syndromic signs indicate acute Bovine Respiratory Disease Complex (BRDC). "
                "Compromised respiratory exchange and potential progression to fibrinous pleuropneumonia "
                "require immediate clinical stabilization."
            )
            immediate_actions = [
                "Isolate affected animal in a dry, well-ventilated recovery stall.",
                "Conduct thoracic auscultation and evaluate lung sound rales.",
                "Separate cohort calves sharing common water troughs.",
                "Provide fresh warm water and palatable green forage."
            ]
            preventive_actions = [
                "Enhance cross-ventilation rate in housing shed to lower aerosol bacterial load.",
                "Administer multivalent BRD vaccine to young stock under 12 months.",
                "Disinfect shared water troughs with 1:1000 potassium permanganate solution."
            ]
            differentials = [
                DifferentialDiagnosisItem(disease="Bovine Respiratory Disease Complex", probability=87.0, rationale="Tachypnea, fever, and purulent nasal discharge."),
                DifferentialDiagnosisItem(disease="Infectious Bovine Rhinotracheitis (IBR)", probability=8.8, rationale="Lower necrotic diphtheritic plaque density on nasal mucosa."),
                DifferentialDiagnosisItem(disease="Aspiration Pneumonia", probability=4.2, rationale="No prior forced drenching or esophageal tubing history.")
            ]
            visual_indicators = [
                "Bilateral mucopurulent nasal discharge",
                "Droopy pinnae (depressed ear posture)",
                "Abdominal effort during expiration"
            ]

        # Evaluate risk dynamically through the Risk Engine
        risk_evaluation = clinical_risk_engine.evaluate_risk(
            condition_name=possible_condition,
            confidence=confidence,
            species=data.species or "Cattle",
            symptoms=data.symptoms,
            temperature=data.temperature,
            appetite=data.appetite,
            activity_level=data.activity_level,
            breathing_condition=data.breathing_condition,
            observations=data.observations
        )

        return {
            "possible_condition": possible_condition,
            "confidence": confidence,
            "risk_level": risk_evaluation["risk_level"],
            "risk_score": risk_evaluation["risk_score"],
            "risk_reasoning": risk_evaluation["risk_reasoning"],
            "contributing_factors": risk_evaluation["contributing_factors"],
            "symptoms_detected": symptoms_detected,
            "symptom_evidence": [s for s in data.symptoms if s in symptoms_detected or any(w in s.lower() for w in ["fever", "discharge", "breath", "salivat", "nodule", "cough"])],
            "detected_visual_indicators": visual_indicators,
            "explanation": explanation,
            "recommended_immediate_actions": immediate_actions,
            "veterinary_review_required": True,
            "preventive_actions": preventive_actions,
            "differential_diagnoses": differentials,
            "is_demo_inference": True,
            "model_version": ai_config.DEMO_MODEL_VERSION
        }

demo_inference_engine = DemoInferenceEngine()
