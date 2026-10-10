"""
AniCare AI — Animal & Clinical Case Grouping Auditor
Ensures animal-level cohort integrity during independent external evaluation.
Adheres strictly to scientific truthfulness:
If animal/patient identifiers are absent, records animal_grouping_available = false.
Never fabricates synthetic IDs or claims herd-independent generalization falsely.
"""

from typing import Dict, Any, List, Set
from collections import defaultdict


class AnimalGroupingAuditor:
    """Manages animal-level and case-level grouping metadata."""

    @classmethod
    def audit_grouping(cls, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Audits animal identifier presence and groups records by unique animal ID.
        """
        if not records:
            return {
                "animal_grouping_available": False,
                "unique_animal_count": 0,
                "missing_identifier_count": 0,
                "total_records": 0,
                "limitation_note": "No records supplied for grouping analysis."
            }

        animal_map = defaultdict(list)
        missing_count = 0

        for r in records:
            aid = r.get("animal_id") or r.get("ear_tag") or r.get("patient_id") or r.get("case_id")
            if aid and str(aid).strip().lower() not in ["none", "null", "unknown", ""]:
                clean_id = str(aid).strip()
                animal_map[clean_id].append(r.get("sample_id") or r.get("image_id"))
            else:
                missing_count += 1

        total = len(records)
        # Required >= 80% coverage to declare grouping available
        has_grouping = len(animal_map) > 0 and (missing_count / max(total, 1)) < 0.20

        return {
            "animal_grouping_available": has_grouping,
            "unique_animal_count": len(animal_map),
            "missing_identifier_count": missing_count,
            "total_records": total,
            "animal_cohorts": {k: len(v) for k, v in animal_map.items()} if has_grouping else {},
            "limitation_note": (
                "Animal grouping verified; partition isolation by patient identity supported."
                if has_grouping else
                "animal_grouping_available = false; animal identifiers absent from source metadata. "
                "The evaluation CANNOT claim herd-independent generalization."
            )
        }


grouping_auditor = AnimalGroupingAuditor()
