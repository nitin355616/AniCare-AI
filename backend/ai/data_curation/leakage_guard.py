"""
AniCare AI — Partition Leakage Guard
Verifies cryptographic separation and animal-level isolation across
Train, Validation, and Held-out Test datasets before training or benchmarking.
"""

from typing import List, Dict, Any, Set, Tuple
from pydantic import BaseModel


class DataLeakageError(Exception):
    """Raised when data leakage is detected across evaluation partitions."""
    pass


class LeakageAuditReport(BaseModel):
    has_leakage: bool
    train_test_overlap_count: int
    train_val_overlap_count: int
    val_test_overlap_count: int
    animal_id_leakage_count: int
    overlapping_hashes: List[str]
    overlapping_animals: List[str]
    details: str


class DatasetLeakageGuard:
    """
    Guarantees absolute scientific isolation of evaluation sets.
    """

    @classmethod
    def audit_partitions(
        cls,
        train_samples: List[Dict[str, Any]],
        val_samples: List[Dict[str, Any]],
        test_samples: List[Dict[str, Any]]
    ) -> LeakageAuditReport:
        """
        Audits cryptographic hashes and animal identifiers across all three partitions.
        """
        train_hashes: Set[str] = {s["sha256"].lower() for s in train_samples if s.get("sha256")}
        val_hashes: Set[str] = {s["sha256"].lower() for s in val_samples if s.get("sha256")}
        test_hashes: Set[str] = {s["sha256"].lower() for s in test_samples if s.get("sha256")}

        train_test_overlap = train_hashes.intersection(test_hashes)
        train_val_overlap = train_hashes.intersection(val_hashes)
        val_test_overlap = val_hashes.intersection(test_hashes)

        # Animal-level grouping checks
        train_animals: Set[str] = {s["animal_id"] for s in train_samples if s.get("animal_id")}
        val_animals: Set[str] = {s["animal_id"] for s in val_samples if s.get("animal_id")}
        test_animals: Set[str] = {s["animal_id"] for s in test_samples if s.get("animal_id")}

        animal_train_test = train_animals.intersection(test_animals)
        animal_train_val = train_animals.intersection(val_animals)
        animal_val_test = val_animals.intersection(test_animals)
        all_animal_leakage = animal_train_test.union(animal_train_val).union(animal_val_test)

        all_hash_leakage = train_test_overlap.union(train_val_overlap).union(val_test_overlap)

        has_leakage = len(all_hash_leakage) > 0 or len(all_animal_leakage) > 0

        details = "PARTITION INTEGRITY VERIFIED: 0% cross-split leakage." if not has_leakage else (
            f"LEAKAGE DETECTED! Hash overlap: {len(all_hash_leakage)}, "
            f"Animal ID overlap: {len(all_animal_leakage)}"
        )

        return LeakageAuditReport(
            has_leakage=has_leakage,
            train_test_overlap_count=len(train_test_overlap),
            train_val_overlap_count=len(train_val_overlap),
            val_test_overlap_count=len(val_test_overlap),
            animal_id_leakage_count=len(all_animal_leakage),
            overlapping_hashes=list(all_hash_leakage),
            overlapping_animals=list(all_animal_leakage),
            details=details
        )

    @classmethod
    def assert_zero_leakage(
        cls,
        train_samples: List[Dict[str, Any]],
        val_samples: List[Dict[str, Any]],
        test_samples: List[Dict[str, Any]]
    ) -> None:
        """Raises DataLeakageError if any cross-partition overlap exists."""
        report = cls.audit_partitions(train_samples, val_samples, test_samples)
        if report.has_leakage:
            raise DataLeakageError(report.details)


dataset_leakage_guard = DatasetLeakageGuard()
