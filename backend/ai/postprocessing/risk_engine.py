"""
AniCare AI — Multi-Modal Clinical Risk Engine
Decoupled multi-modal veterinary triage and risk-scoring layer conforming to OIE/ICAR guidelines.
Synthesizes:
1. Visual Risk (vision confidence, lesion visibility, image quality)
2. Symptom Risk (cutaneous nodules, lymphadenopathy, salivation, lameness, milk drop)
3. Physiological Risk (core pyrexia, tachypnea, heart rate anomalies)
4. Epidemiological Risk (herd cases, spatial clusters, animal movement history)
5. Animal History Risk (vaccination status, age tier, naive herd susceptibility)

IMPORTANT REGULATORY & SAFETY PRINCIPLES:
- Decouples visual confidence from clinical risk.
- Explicitly outputs operational 'risk score' (0-100), NOT a 'confirmed disease probability'.
- Never prescribes medication, calculates drug dosage, or asserts medical certainty.
- Mandatory veterinary physical review required on all early-warning tiers.
"""

from typing import Dict, Any, List, Optional
import re


class ClinicalRiskEngine:
    """
    Transparent, explainable multi-modal veterinary early-warning risk engine.
    """

    # Inherent condition pathology tiers
    EPIZOOTIC_CRITICAL_CONDITIONS = [
        "foot and mouth disease",
        "anthrax",
        "rinderpest",
        "african swine fever",
        "rabies",
        "black quarter",
        "bovine pleuropneumonia"
    ]

    HIGH_SYSTEMIC_CONDITIONS = [
        "lumpy skin disease",
        "respiratory infection",
        "bovine respiratory disease",
        "acute bronchopneumonia",
        "acute mastitis",
        "haemorrhagic septicaemia",
        "theileriosis"
    ]

    MILD_LOCALIZED_CONDITIONS = [
        "ringworm",
        "dermatophytosis",
        "subclinical mastitis",
        "papilloma",
        "warts",
        "mild conjunctivitis",
        "superficial dermatitis",
        "healthy / normal",
        "normal"
    ]

    @classmethod
    def parse_temperature(cls, temp_str: Optional[str]) -> Optional[float]:
        """Extracts float temperature value from strings like '104.8 °F' or '104.8'."""
        if not temp_str:
            return None
        match = re.search(r"(\d+(\.\d+)?)", str(temp_str))
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                return None
        return None

    @classmethod
    def evaluate_risk(
        cls,
        condition_name: str,
        confidence: float,
        species: str = "Cattle",
        symptoms: Optional[List[str]] = None,
        temperature: Optional[str] = None,
        appetite: Optional[str] = None,
        activity_level: Optional[str] = None,
        breathing_condition: Optional[str] = None,
        observations: Optional[str] = None,
        # Multi-modal extensions:
        heart_rate: Optional[float] = None,
        respiratory_rate: Optional[float] = None,
        vaccination_status: Optional[str] = "UNKNOWN",
        age_months: Optional[int] = None,
        recent_nearby_cases: Optional[int] = 0,
        herd_at_risk_count: Optional[int] = 0,
        cluster_warning_active: Optional[bool] = False,
        recent_movement: Optional[bool] = False,
        image_quality: Optional[str] = "ADEQUATE"
    ) -> Dict[str, Any]:
        """
        Calculates multi-modal risk scores and overall early-warning escalation tier.
        """
        symptoms_list = symptoms or []
        symptoms_text = " ".join(symptoms_list).lower()
        condition_lower = condition_name.lower()
        temp_val = cls.parse_temperature(temperature)

        reasoning_list: List[str] = []
        contributing_factors: List[str] = []
        escalation_flags: List[str] = []

        # =====================================================================
        # 1. VISUAL RISK SCORE (0 - 100)
        # =====================================================================
        visual_score = 0.0
        is_healthy_visual = "healthy" in condition_lower or "normal" in condition_lower

        if is_healthy_visual:
            visual_score = max(5.0, 100.0 - confidence) * 0.30
            reasoning_list.append(f"Visual scan: No characteristic cutaneous lesion detected (Healthy confidence {confidence:.1f}%).")
        else:
            if any(c in condition_lower for c in cls.EPIZOOTIC_CRITICAL_CONDITIONS):
                visual_score = min(100.0, 60.0 + (confidence * 0.40))
                factor = f"Visual identification of notifiable epizootic: {condition_name}"
                contributing_factors.append(factor)
                reasoning_list.append(factor)
            elif any(c in condition_lower for c in cls.HIGH_SYSTEMIC_CONDITIONS):
                visual_score = min(100.0, 45.0 + (confidence * 0.40))
                factor = f"Visual identification of contagious condition: {condition_name}"
                contributing_factors.append(factor)
                reasoning_list.append(factor)
            else:
                visual_score = min(60.0, 20.0 + (confidence * 0.30))
                reasoning_list.append(f"Visual identification of localized condition: {condition_name}.")

        # Image quality mitigation
        if str(image_quality).upper() in ["LOW", "POOR", "DEGRADED"]:
            visual_score *= 0.85
            reasoning_list.append("Visual confidence discounted due to suboptimal image quality.")

        # =====================================================================
        # 2. SYMPTOM RISK SCORE (0 - 100)
        # =====================================================================
        symptom_score = 10.0
        symptom_factors: List[str] = []

        # High-risk contagious lesion signs
        if any(s in symptoms_text for s in ["nodule", "cutaneous nodule", "skin lump", "lumpy"]):
            symptom_score += 25.0
            symptom_factors.append("Cutaneous dermal nodules")
        if any(s in symptoms_text for s in ["vesicle", "vesicular", "ulcer", "erosion", "salivation", "drool"]):
            symptom_score += 30.0
            symptom_factors.append("Oral/coronary vesicular lesions or ropy sialorrhea")
        if any(s in symptoms_text for s in ["respiratory", "dyspneic", "dyspnea", "nasal", "discharge", "cough", "shallow"]):
            symptom_score += 25.0
            symptom_factors.append("Respiratory distress / nasal discharge")
        if any(s in symptoms_text for s in ["pyrexia", "fever", "hyperthermia"]):
            symptom_score += 15.0
            symptom_factors.append("Reported febrile state")
        if any(s in symptoms_text for s in ["lymph", "swollen lymph", "lymphadenopathy"]):
            symptom_score += 18.0
            symptom_factors.append("Enlarged superficial lymph nodes")
        if any(s in symptoms_text for s in ["mastitis", "clot", "floccule", "udder swell"]):
            symptom_score += 20.0
            symptom_factors.append("Mammary induration / milk floccules")
        if any(s in symptoms_text for s in ["lame", "lameness", "coronary band"]):
            symptom_score += 15.0
            symptom_factors.append("Locomotor lameness")
        if any(s in symptoms_text for s in ["milk drop", "reduced milk", "yield loss"]):
            symptom_score += 12.0
            symptom_factors.append("Abrupt milk yield depression")

        # Appetite loss
        appetite_str = str(appetite or "").lower()
        if any(a in appetite_str for a in ["severely reduced", "complete refusal", "anorexia"]):
            symptom_score += 15.0
            symptom_factors.append("Severe anorexia")
        elif any(a in appetite_str for a in ["reduced", "depressed", "poor", "inappetence"]):
            symptom_score += 8.0
            symptom_factors.append("Depressed appetite")

        # Activity / Lethargy
        activity_str = str(activity_level or "").lower()
        if any(act in activity_str or act in symptoms_text for act in ["downer", "recumbent", "collapse"]):
            symptom_score += 25.0
            symptom_factors.append("Recumbent downer state")
            escalation_flags.append("ANIMAL_RECUMBENT")
        elif "lethargic" in activity_str:
            symptom_score += 10.0

        symptom_score = min(100.0, max(0.0, symptom_score))
        if symptom_factors:
            contributing_factors.extend(symptom_factors)
            reasoning_list.append(f"Symptom profile flagged: {', '.join(symptom_factors)}.")

        # =====================================================================
        # 3. PHYSIOLOGICAL RISK SCORE (0 - 100)
        # =====================================================================
        phys_score = 10.0
        phys_factors: List[str] = []

        # Bovine normal temperature: 100.4°F - 102.8°F
        if temp_val is not None:
            if temp_val >= 105.0:
                phys_score += 45.0
                phys_factors.append(f"Severe Hyperpyrexia ({temp_val}°F >= 105.0°F)")
                escalation_flags.append("SEVERE_HYPERPYREXIA")
            elif temp_val >= 103.5:
                phys_score += 25.0
                phys_factors.append(f"Marked Pyrexia ({temp_val}°F >= 103.5°F)")
            elif temp_val >= 102.9:
                phys_score += 12.0
                phys_factors.append(f"Low-grade Pyrexia ({temp_val}°F)")
            elif temp_val < 99.5:
                phys_score += 30.0
                phys_factors.append(f"Hypothermia ({temp_val}°F < 99.5°F) indicating circulatory collapse")
                escalation_flags.append("HYPOTHERMIA_SHOCK")

        # Respiratory condition / tachypnea
        breathing_str = str(breathing_condition or "").lower()
        if any(b in breathing_str or b in symptoms_text for b in ["dyspneic", "dyspnea", "labored", "gasping"]):
            phys_score += 20.0
            phys_factors.append("Labored dyspneic respiration")
        elif "rapid" in breathing_str:
            phys_score += 10.0

        if respiratory_rate is not None and respiratory_rate > 50:
            phys_score += 15.0
            phys_factors.append(f"Tachypnea ({respiratory_rate} breaths/min > 50)")

        if heart_rate is not None and (heart_rate > 90 or heart_rate < 40):
            phys_score += 15.0
            phys_factors.append(f"Abnormal heart rate ({heart_rate} bpm)")

        phys_score = min(100.0, max(0.0, phys_score))
        if phys_factors:
            contributing_factors.extend(phys_factors)
            reasoning_list.append(f"Physiological vitals: {', '.join(phys_factors)}.")

        # =====================================================================
        # 4. EPIDEMIOLOGICAL RISK SCORE (0 - 100)
        # =====================================================================
        epi_score = 10.0
        epi_factors: List[str] = []

        if cluster_warning_active:
            epi_score += 35.0
            epi_factors.append("Active spatial early-warning cluster in village/block")
            escalation_flags.append("CLUSTER_ACTIVE")

        if recent_nearby_cases and recent_nearby_cases > 0:
            boost = min(30.0, recent_nearby_cases * 6.0)
            epi_score += boost
            epi_factors.append(f"{recent_nearby_cases} confirmed/suspected cases in 10km radius")

        if herd_at_risk_count and herd_at_risk_count >= 3:
            epi_score += 20.0
            epi_factors.append(f"{herd_at_risk_count} cohabitating herd members displaying concurrent illness")
            escalation_flags.append("HERD_COHORT_SPREAD")

        if recent_movement:
            epi_score += 15.0
            epi_factors.append("Recent animal transit or introduction from livestock market")

        epi_score = min(100.0, max(0.0, epi_score))
        if epi_factors:
            contributing_factors.extend(epi_factors)
            reasoning_list.append(f"Epidemiological context: {', '.join(epi_factors)}.")

        # =====================================================================
        # 5. ANIMAL HISTORY RISK SCORE (0 - 100)
        # =====================================================================
        hist_score = 15.0
        hist_factors: List[str] = []

        vac_status = str(vaccination_status or "UNKNOWN").upper()
        if vac_status == "UNVACCINATED":
            hist_score += 25.0
            hist_factors.append("Unvaccinated status against regional epizootics")
        elif vac_status == "UNKNOWN":
            hist_score += 12.0
            hist_factors.append("Unverified vaccination status")
        elif vac_status == "VACCINATED":
            hist_score = max(5.0, hist_score - 10.0)

        # Naive age tier (young calves <6 months or high-yield periparturient cows)
        if age_months is not None and age_months < 12:
            hist_score += 15.0
            hist_factors.append(f"Juvenile cohort vulnerability ({age_months} months old)")

        hist_score = min(100.0, max(0.0, hist_score))
        if hist_factors:
            reasoning_list.append(f"History context: {', '.join(hist_factors)}.")

        # =====================================================================
        # 6. COMPOSITE OVERALL RISK SCORE & ESCALATION RULES
        # =====================================================================
        # Weighted multi-modal fusion:
        # Visual: 30%, Symptoms: 25%, Physiology: 20%, Epidemiology: 15%, History: 10%
        overall_score = (
            (visual_score * 0.30) +
            (symptom_score * 0.25) +
            (phys_score * 0.20) +
            (epi_score * 0.15) +
            (hist_score * 0.10)
        )

        # Critical Escalation Overrides:
        # If Severe Hyperpyrexia + Cutaneous Nodules + Active Cluster -> Escalates directly to CRITICAL
        if "SEVERE_HYPERPYREXIA" in escalation_flags and any(s in symptoms_text for s in ["nodule", "vesic"]):
            overall_score = max(overall_score, 88.0)
            reasoning_list.append("CRITICAL ESCALATION: Severe fever combined with acute cutaneous/vesicular pathology.")

        if "HERD_COHORT_SPREAD" in escalation_flags and overall_score >= 50.0:
            overall_score = max(overall_score, 78.0)
            reasoning_list.append("HIGH ESCALATION: Multiple sick cohort animals in shared pen.")

        # Baseline pathological anchor: High systemic conditions with marked clinical signs must maintain clinical risk tier
        if any(c in condition_lower for c in cls.HIGH_SYSTEMIC_CONDITIONS) and not is_healthy_visual:
            if (temp_val and temp_val >= 103.0) or len(contributing_factors) >= 2:
                overall_score = max(overall_score, 65.0)
                reasoning_list.append("HIGH SYSTEMIC ESCALATION: Contagious systemic condition with pyrexia/clinical distress.")
        elif any(c in condition_lower for c in cls.EPIZOOTIC_CRITICAL_CONDITIONS) and not is_healthy_visual:
            overall_score = max(overall_score, 88.0)
            reasoning_list.append("CRITICAL EPIZOOTIC ESCALATION: Notifiable transboundary animal disease detected.")

        # Mild localized cap guard
        if any(c in condition_lower for c in cls.MILD_LOCALIZED_CONDITIONS) and not phys_factors and not epi_factors:
            overall_score = min(overall_score, 40.0)

        overall_score = round(max(0.0, min(100.0, overall_score)), 1)

        # Tiers: CRITICAL (>=85), HIGH (>=60), MODERATE (>=35), LOW (<35)
        if overall_score >= 85.0:
            risk_level = "CRITICAL"
            urgency = "IMMEDIATE_QUARANTINE"
        elif overall_score >= 60.0:
            risk_level = "HIGH"
            urgency = "URGENT_24H"
        elif overall_score >= 35.0:
            risk_level = "MODERATE"
            urgency = "OBSERVATION_48H"
        else:
            risk_level = "LOW"
            urgency = "ROUTINE_MONITORING"

        return {
            # Core backward-compatible fields
            "risk_level": risk_level,
            "risk_score": overall_score,
            "urgency": urgency,
            "risk_reasoning": " | ".join(reasoning_list),
            "contributing_factors": contributing_factors,
            "veterinary_review_required": True,
            # Enhanced multi-modal breakdown fields
            "visual_risk_score": round(visual_score, 1),
            "symptom_risk_score": round(symptom_score, 1),
            "physiological_risk_score": round(phys_score, 1),
            "epidemiological_risk_score": round(epi_score, 1),
            "history_risk_score": round(hist_score, 1),
            "overall_risk_score": overall_score,
            "risk_reasoning_list": reasoning_list,
            "escalation_flags": escalation_flags
        }


clinical_risk_engine = ClinicalRiskEngine()
