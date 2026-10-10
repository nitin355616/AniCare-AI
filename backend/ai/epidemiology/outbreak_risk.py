"""
AniCare AI — Herd Outbreak Risk Evaluator
Calculates velocity of transmission, vaccination coverage deficits,
and biosecurity containment urgency for detected disease clusters.
"""

from typing import Dict, Any, List
from pydantic import BaseModel


class OutbreakRiskProfile(BaseModel):
    """Outbreak risk rating for an emergent cluster."""
    cluster_id: str
    outbreak_risk_tier: str  # "LOW_VIGILANCE" | "ELEVATED_SURVEILLANCE" | "HIGH_RISK_CLUSTER" | "CRITICAL_BIOSECURITY_CONTAINMENT"
    transmission_velocity: str  # "STABLE" | "MODERATE_PROGRESSION" | "RAPID_COHORT_SPREAD"
    estimated_reproduction_index: float
    containment_recommendation: List[str]
    veterinary_action_required: str


class HerdOutbreakRiskEvaluator:
    """
    Evaluates epidemiological risk metrics for livestock clusters.
    Enforces precautionary biosecurity containment.
    """

    @classmethod
    def evaluate_cluster_risk(
        cls,
        total_animals: int,
        high_critical_count: int,
        condition: str,
        unvaccinated_ratio: float = 0.50
    ) -> OutbreakRiskProfile:
        cond_lower = condition.lower()
        is_epizootic = any(c in cond_lower for c in ["lumpy", "foot and mouth", "fmd", "capripox", "anthrax"])

        # Transmission velocity
        if total_animals >= 6 or high_critical_count >= 4:
            velocity = "RAPID_COHORT_SPREAD"
            r_est = 2.4
        elif total_animals >= 3 or high_critical_count >= 2:
            velocity = "MODERATE_PROGRESSION"
            r_est = 1.6
        else:
            velocity = "STABLE"
            r_est = 1.1

        # Outbreak risk tier
        if is_epizootic and (velocity == "RAPID_COHORT_SPREAD" or unvaccinated_ratio >= 0.40):
            tier = "CRITICAL_BIOSECURITY_CONTAINMENT"
            vet_action = "Immediate District Veterinary Officer (DVO) emergency dispatch & 5km ring vaccination."
            actions = [
                "Establish 100-meter immediate standoff quarantine around affected pens.",
                "Halt outward movements of livestock, milk tankers, and farm vehicles.",
                "Institute emergency vector fogging against Stomoxys / Tabanid flies.",
                "Notify State Animal Husbandry Department (DAHD) control room."
            ]
        elif is_epizootic or high_critical_count >= 2:
            tier = "HIGH_RISK_CLUSTER"
            vet_action = "Priority veterinary on-site visit within 12 hours for clinical sample collection."
            actions = [
                "Isolate symptomatic cattle in recovery paddocks under insect-proof mesh.",
                "Inspect all cohort dairy cows sharing common water troughs.",
                "Daily body temperature logging across the entire herd.",
                "Disinfect shed entryways with 4% sodium carbonate."
            ]
        else:
            tier = "ELEVATED_SURVEILLANCE"
            vet_action = "Routine tele-veterinary follow-up and clinical syndromic tracking."
            actions = [
                "Continue twice-daily observational checks for nodular or mucosal eruptions.",
                "Maintain baseline dairy hygiene."
            ]

        return OutbreakRiskProfile(
            cluster_id="",
            outbreak_risk_tier=tier,
            transmission_velocity=velocity,
            estimated_reproduction_index=round(r_est, 2),
            containment_recommendation=actions,
            veterinary_action_required=vet_action
        )


outbreak_risk_evaluator = HerdOutbreakRiskEvaluator()
