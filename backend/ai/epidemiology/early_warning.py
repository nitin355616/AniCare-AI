"""
AniCare AI — National Early-Warning Intelligence Service
Aggregates multi-animal assessment signals, detects spatial clusters,
and publishes early-warning event dossiers for field veterinary response.
"""

from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

try:
    from ai.epidemiology.cluster_detector import cluster_detector, SpatialTemporalCluster
    from ai.epidemiology.outbreak_risk import outbreak_risk_evaluator, OutbreakRiskProfile
except ImportError:
    from backend.ai.epidemiology.cluster_detector import cluster_detector, SpatialTemporalCluster
    from backend.ai.epidemiology.outbreak_risk import outbreak_risk_evaluator, OutbreakRiskProfile


class EarlyWarningEvent(BaseModel):
    """Structured Early Warning Event conforming to SIH 2026 national specifications."""
    signal_id: str
    signal_type: str = "EARLY_WARNING_SIGNAL"
    cluster_classification: str  # "POSSIBLE_CLUSTER" | "HIGH_RISK_CLUSTER"
    suspected_condition: str
    target_species: str
    location: Dict[str, str]
    time_window: Dict[str, str]
    cluster_size: int
    high_critical_count: int
    severity_level: str  # "ELEVATED", "HIGH", "CRITICAL"
    confidence_score: float
    affected_animals: List[str]
    recommended_veterinary_action: str
    containment_protocol: List[str]
    is_simulated_demo_data: bool = False
    disclaimer: str
    created_at: str


class EarlyWarningService:
    """
    Central orchestration service for epizootic early-warning surveillance.
    """

    DISCLAIMER_TEXT = (
        "AI-ASSISTED EARLY-WARNING SIGNAL: Indicates an emergent spatial cluster of suspect animal cases. "
        "Does NOT represent a legally confirmed disease outbreak without regulatory laboratory confirmation "
        "(e.g., RT-PCR/ELISA) and authorized declaration by the State Department of Animal Husbandry."
    )

    @classmethod
    def generate_early_warning_events(
        cls,
        assessments: List[Dict[str, Any]]
    ) -> List[EarlyWarningEvent]:
        """
        Analyzes live livestock assessments, clusters nearby at-risk animals,
        and generates formal EarlyWarningEvent signals.
        """
        raw_clusters: List[SpatialTemporalCluster] = cluster_detector.detect_clusters(assessments)
        events: List[EarlyWarningEvent] = []

        now_iso = datetime.now(timezone.utc).isoformat()

        for c in raw_clusters:
            risk_prof: OutbreakRiskProfile = outbreak_risk_evaluator.evaluate_cluster_risk(
                total_animals=c.total_animals,
                high_critical_count=c.high_critical_count,
                condition=c.condition
            )

            severity = "CRITICAL" if "CRITICAL" in risk_prof.outbreak_risk_tier else (
                "HIGH" if "HIGH" in risk_prof.outbreak_risk_tier else "ELEVATED"
            )

            event = EarlyWarningEvent(
                signal_id=f"SIG-{c.cluster_id}",
                signal_type="EARLY_WARNING_SIGNAL",
                cluster_classification=c.signal_status,
                suspected_condition=c.condition,
                target_species=c.species,
                location={
                    "state": c.state,
                    "district": c.district,
                    "village_or_town": c.village_or_town
                },
                time_window={
                    "start": c.window_start,
                    "end": c.window_end
                },
                cluster_size=c.total_animals,
                high_critical_count=c.high_critical_count,
                severity_level=severity,
                confidence_score=c.cluster_score,
                affected_animals=[m.animal_id for m in c.members],
                recommended_veterinary_action=risk_prof.veterinary_action_required,
                containment_protocol=risk_prof.containment_recommendation,
                is_simulated_demo_data=False,
                disclaimer=cls.DISCLAIMER_TEXT,
                created_at=now_iso
            )
            events.append(event)

        return events

    @classmethod
    def get_dashboard_early_warning_feed(
        cls,
        live_assessments: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Returns live signals fused with clearly-tagged realistic demo signals
        for SIH national hackathon demonstration.
        """
        live_events = cls.generate_early_warning_events(live_assessments or [])

        # Realistic simulated demo signals clearly flagged as demo data
        demo_events = [
            EarlyWarningEvent(
                signal_id="SIG-DEMO-GJ-001",
                signal_type="EARLY_WARNING_SIGNAL",
                cluster_classification="HIGH_RISK_CLUSTER",
                suspected_condition="Lumpy Skin Disease (Capripox)",
                target_species="Cattle",
                location={"state": "Gujarat", "district": "Anand", "village_or_town": "Boriavi"},
                time_window={"start": "2026-10-01", "end": "2026-10-07"},
                cluster_size=7,
                high_critical_count=5,
                severity_level="CRITICAL",
                confidence_score=86.4,
                affected_animals=["AN-GJ-0104", "AN-GJ-0109", "AN-GJ-0112", "AN-GJ-0125", "AN-GJ-0131"],
                recommended_veterinary_action="Immediate District Veterinary Officer (DVO) emergency dispatch & 5km ring vaccination.",
                containment_protocol=[
                    "Establish 100-meter immediate standoff quarantine around affected dairy sheds.",
                    "Halt outward movements of livestock, milk tankers, and farm vehicles.",
                    "Institute emergency vector fogging against Stomoxys / Tabanid flies."
                ],
                is_simulated_demo_data=True,
                disclaimer="DEMO / SIMULATED DATA: Prototype cluster simulation for SIH 2026 early-warning dashboard.",
                created_at="2026-10-07T08:30:00Z"
            ),
            EarlyWarningEvent(
                signal_id="SIG-DEMO-RJ-002",
                signal_type="EARLY_WARNING_SIGNAL",
                cluster_classification="POSSIBLE_CLUSTER",
                suspected_condition="Foot and Mouth Disease (Suspected Vesicular Phase)",
                target_species="Cattle",
                location={"state": "Rajasthan", "district": "Barmer", "village_or_town": "Sindhari"},
                time_window={"start": "2026-10-03", "end": "2026-10-08"},
                cluster_size=4,
                high_critical_count=3,
                severity_level="HIGH",
                confidence_score=78.2,
                affected_animals=["AN-RJ-0220", "AN-RJ-0223", "AN-RJ-0229"],
                recommended_veterinary_action="Priority on-site veterinary verification and ring vaccination advisory.",
                containment_protocol=[
                    "Isolate symptomatic cows in recovery paddocks.",
                    "Apply 4% sodium carbonate footbaths at barn entryways.",
                    "Daily core body temperature logging across herd."
                ],
                is_simulated_demo_data=True,
                disclaimer="DEMO / SIMULATED DATA: Prototype cluster simulation for SIH 2026 early-warning dashboard.",
                created_at="2026-10-08T04:15:00Z"
            )
        ]

        all_signals = live_events + demo_events
        return {
            "total_active_signals": len(all_signals),
            "live_signal_count": len(live_events),
            "simulated_demo_count": len(demo_events),
            "critical_signals": sum(1 for s in all_signals if s.severity_level == "CRITICAL"),
            "high_signals": sum(1 for s in all_signals if s.severity_level == "HIGH"),
            "signals": [s.model_dump() for s in all_signals],
            "disclaimer": cls.DISCLAIMER_TEXT
        }


early_warning_service = EarlyWarningService()
