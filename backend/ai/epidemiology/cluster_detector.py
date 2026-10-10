"""
AniCare AI — Spatial-Temporal Cluster Detector
Identifies emergent disease clusters across farms, villages, and herds
within sliding temporal windows conforming to national epizootic surveillance protocols.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class ClusterMember(BaseModel):
    """Individual animal assessment participating in a cluster."""
    animal_id: str
    assessment_id: str
    risk_level: str  # LOW, MODERATE, HIGH, CRITICAL
    risk_score: float
    timestamp: str
    owner_id: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class SpatialTemporalCluster(BaseModel):
    """Identified multi-animal disease cluster signal."""
    cluster_id: str
    condition: str
    species: str
    state: str
    district: str
    village_or_town: str
    window_start: str
    window_end: str
    total_animals: int
    high_critical_count: int
    cluster_score: float
    signal_status: str  # "EMERGING_SIGNAL" | "POSSIBLE_CLUSTER" | "HIGH_RISK_CLUSTER"
    members: List[ClusterMember]


class SpatialTemporalClusterDetector:
    """
    Detects spatial-temporal disease groupings across livestock populations.
    Precautionary Rule: 3+ animals displaying MODERATE/HIGH/CRITICAL risk
    in the same village/district within 14 days triggers a 'POSSIBLE_CLUSTER'.
    """

    def __init__(self, time_window_days: int = 14, min_cluster_size: int = 3):
        self.time_window_days = time_window_days
        self.min_cluster_size = min_cluster_size

    def detect_clusters(
        self,
        assessments: List[Dict[str, Any]]
    ) -> List[SpatialTemporalCluster]:
        """
        Groups assessments by (district, village, species, condition)
        and evaluates temporal proximity.
        """
        # 1. Group records
        grouped: Dict[str, List[Dict[str, Any]]] = {}
        for a in assessments:
            condition = a.get("possible_condition", "Unknown")
            # Normalize condition key (e.g. Lumpy Skin Disease variants)
            cond_key = "Lumpy Skin Disease" if "lumpy" in condition.lower() else condition
            species = a.get("species", "Cattle")
            district = a.get("district", "General")
            village = a.get("village", a.get("village_or_town", "General"))

            group_key = f"{district}|{village}|{species}|{cond_key}"
            if group_key not in grouped:
                grouped[group_key] = []
            grouped[group_key].append(a)

        detected_clusters: List[SpatialTemporalCluster] = []
        cluster_idx = 1

        for group_key, records in grouped.items():
            if len(records) < self.min_cluster_size:
                continue

            parts = group_key.split("|")
            district, village, species, cond_key = parts[0], parts[1], parts[2], parts[3]

            # Filter for at-risk animals (MODERATE, HIGH, CRITICAL)
            at_risk = [r for r in records if str(r.get("risk_level", "")).upper() in ["MODERATE", "HIGH", "CRITICAL"]]
            if len(at_risk) < self.min_cluster_size:
                continue

            # Sort by timestamp
            def parse_ts(x):
                ts = x.get("created_at", x.get("timestamp", "2026-01-01T00:00:00Z"))
                try:
                    return datetime.fromisoformat(ts.replace("Z", "+00:00"))
                except Exception:
                    return datetime.min

            at_risk.sort(key=parse_ts)
            earliest_dt = parse_ts(at_risk[0])
            latest_dt = parse_ts(at_risk[-1])

            # Check time delta
            if (latest_dt - earliest_dt).days > self.time_window_days * 2:
                # Outside sliding window
                continue

            high_crit_count = sum(1 for r in at_risk if str(r.get("risk_level", "")).upper() in ["HIGH", "CRITICAL"])
            scores = [float(r.get("risk_score", 50.0)) for r in at_risk]
            mean_score = sum(scores) / len(scores)

            if len(at_risk) >= 5 or high_crit_count >= 3:
                signal_status = "HIGH_RISK_CLUSTER"
            else:
                signal_status = "POSSIBLE_CLUSTER"

            members = [
                ClusterMember(
                    animal_id=r.get("animal_id", f"AN-UNK-{i}"),
                    assessment_id=r.get("assessment_id", f"ASM-{i}"),
                    risk_level=r.get("risk_level", "MODERATE"),
                    risk_score=float(r.get("risk_score", 50.0)),
                    timestamp=str(r.get("created_at", r.get("timestamp", ""))),
                    owner_id=r.get("owner_id"),
                    latitude=r.get("latitude"),
                    longitude=r.get("longitude")
                )
                for i, r in enumerate(at_risk)
            ]

            cluster = SpatialTemporalCluster(
                cluster_id=f"CLUS-{district[:3].upper()}-{cluster_idx:03d}",
                condition=cond_key,
                species=species,
                state=records[0].get("state", "Gujarat"),
                district=district,
                village_or_town=village,
                window_start=earliest_dt.strftime("%Y-%m-%d"),
                window_end=latest_dt.strftime("%Y-%m-%d"),
                total_animals=len(at_risk),
                high_critical_count=high_crit_count,
                cluster_score=round(mean_score, 1),
                signal_status=signal_status,
                members=members
            )
            detected_clusters.append(cluster)
            cluster_idx += 1

        return detected_clusters


cluster_detector = SpatialTemporalClusterDetector()
