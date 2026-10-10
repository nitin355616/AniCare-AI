"""
AniCare AI — Dataset Manifest Manager
Handles loading, saving (JSON/CSV), animal-level group partitioning (preventing same-animal leakage),
and exporting standardized validation reports.
"""

import os
import json
import csv
import random
from typing import List, Dict, Any, Optional
from collections import defaultdict

try:
    from ai.dataset.schema import DatasetManifestRecord, DatasetSplitEnum
    from ai.dataset.validator import DatasetManifestValidator
except ImportError:
    from backend.ai.dataset.schema import DatasetManifestRecord, DatasetSplitEnum
    from backend.ai.dataset.validator import DatasetManifestValidator


class DatasetManifestManager:
    """
    Manages manifest input/output and guarantees animal-level split isolation.
    """

    @staticmethod
    def load_from_json(file_path: str) -> List[DatasetManifestRecord]:
        """Loads and parses a JSON list of manifest records."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Manifest file not found: {file_path}")
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            raise ValueError(f"Manifest root must be a JSON array, got {type(data)}")
        return [DatasetManifestRecord.model_validate(item) for item in data]

    @staticmethod
    def save_to_json(records: List[DatasetManifestRecord], file_path: str) -> None:
        """Saves a list of manifest records to a formatted JSON file."""
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        data = [rec.model_dump(mode="json") for rec in records]
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    @staticmethod
    def load_from_csv(file_path: str) -> List[DatasetManifestRecord]:
        """Loads and parses a CSV manifest file."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"CSV manifest not found: {file_path}")
        records: List[DatasetManifestRecord] = []
        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                cleaned = {k: v for k, v in row.items() if v != ""}
                records.append(DatasetManifestRecord.model_validate(cleaned))
        return records

    @staticmethod
    def save_to_csv(records: List[DatasetManifestRecord], file_path: str) -> None:
        """Saves records to CSV with standard schema column headers."""
        if not records:
            return
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        fields = list(records[0].model_dump().keys())
        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            for rec in records:
                writer.writerow(rec.model_dump(mode="json"))

    @staticmethod
    def split_by_animal(
        records: List[DatasetManifestRecord],
        train_ratio: float = 0.70,
        val_ratio: float = 0.15,
        test_ratio: float = 0.15,
        seed: int = 42
    ) -> List[DatasetManifestRecord]:
        """
        Partitions dataset records by animal_id grouping.
        CRITICAL VETERINARY ML RULE: All images of the same individual animal MUST
        reside entirely in train, val, OR test. They must NEVER cross split boundaries.
        """
        if abs((train_ratio + val_ratio + test_ratio) - 1.0) > 1e-4:
            raise ValueError("Split ratios must sum to 1.0 (train + val + test).")

        # Group records by animal_id (or image_id fallback if animal_id absent)
        animal_groups: Dict[str, List[DatasetManifestRecord]] = defaultdict(list)
        for rec in records:
            group_key = rec.animal_id.strip() if rec.animal_id and rec.animal_id.strip() else f"IMG_GRP_{rec.image_id}"
            animal_groups[group_key].append(rec)

        unique_animals = sorted(list(animal_groups.keys()))
        rng = random.Random(seed)
        rng.shuffle(unique_animals)

        n_animals = len(unique_animals)
        n_train = int(n_animals * train_ratio)
        n_val = int(n_animals * val_ratio)

        train_animals = set(unique_animals[:n_train])
        val_animals = set(unique_animals[n_train:n_train + n_val])
        test_animals = set(unique_animals[n_train + n_val:])

        # Reassign split field on cloned records
        partitioned_records: List[DatasetManifestRecord] = []
        for anim, group in animal_groups.items():
            if anim in train_animals:
                target_split = DatasetSplitEnum.TRAIN
            elif anim in val_animals:
                target_split = DatasetSplitEnum.VALIDATION
            else:
                target_split = DatasetSplitEnum.TEST

            for rec in group:
                cloned = rec.model_copy(update={"split": target_split})
                partitioned_records.append(cloned)

        return partitioned_records

    @staticmethod
    def export_validation_report(report_data: Dict[str, Any], output_path: str) -> str:
        """Exports validation report dictionary to dataset_report.json."""
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        return output_path
