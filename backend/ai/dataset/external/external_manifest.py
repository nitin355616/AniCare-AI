"""
AniCare AI — External Dataset Manifest (Immutable Record Model)
Defines schema and serialization for independently acquired external evaluation datasets.
Never stores raw personally identifying information (anonymizes animal/case IDs via SHA-256).
"""

import json
import hashlib
from pathlib import Path
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class ExternalManifestRecord(BaseModel):
    """Immutable record schema for an external dataset image."""
    image_id: str
    source_id: str
    species: str
    ground_truth: str
    clinical_condition: str
    image_path: str
    sha256: str
    image_width: int
    image_height: int
    license_status: str
    permission_status: str
    animal_id_hash: Optional[str] = None
    case_id_hash: Optional[str] = None
    collection_date_if_allowed: Optional[str] = None
    location_level_if_allowed: Optional[str] = None
    quality_status: str
    duplicate_status: str
    split: str = "external_test"
    notes: str = ""

    @classmethod
    def create_sanitized(
        cls,
        image_id: str,
        source_id: str,
        species: str,
        ground_truth: str,
        clinical_condition: str,
        image_path: str,
        sha256: str,
        image_width: int,
        image_height: int,
        license_status: str,
        permission_status: str,
        raw_animal_id: Optional[str] = None,
        raw_case_id: Optional[str] = None,
        collection_date: Optional[str] = None,
        location_level: Optional[str] = None,
        quality_status: str = "ACCEPTABLE",
        duplicate_status: str = "UNIQUE",
        split: str = "external_test",
        notes: str = ""
    ) -> "ExternalManifestRecord":
        """
        Creates a sanitized record, cryptographically hashing animal/case IDs
        to strictly protect herd and farmer privacy.
        """
        animal_hash = None
        if raw_animal_id and str(raw_animal_id).strip().lower() not in ["none", "null", "unknown", ""]:
            animal_hash = hashlib.sha256(str(raw_animal_id).strip().encode()).hexdigest()[:16]

        case_hash = None
        if raw_case_id and str(raw_case_id).strip().lower() not in ["none", "null", "unknown", ""]:
            case_hash = hashlib.sha256(str(raw_case_id).strip().encode()).hexdigest()[:16]

        return cls(
            image_id=image_id,
            source_id=source_id,
            species=species,
            ground_truth=ground_truth,
            clinical_condition=clinical_condition,
            image_path=image_path,
            sha256=sha256,
            image_width=image_width,
            image_height=image_height,
            license_status=license_status,
            permission_status=permission_status,
            animal_id_hash=animal_hash,
            case_id_hash=case_hash,
            collection_date_if_allowed=collection_date,
            location_level_if_allowed=location_level,
            quality_status=quality_status,
            duplicate_status=duplicate_status,
            split=split,
            notes=notes
        )


class ExternalDatasetManifest:
    """Manages collection of external manifest records and persistence."""

    def __init__(self, records: Optional[List[ExternalManifestRecord]] = None):
        self.records: List[ExternalManifestRecord] = records or []

    def add_record(self, record: ExternalManifestRecord):
        self.records.append(record)

    def to_json(self) -> List[Dict[str, Any]]:
        return [r.model_dump() for r in self.records]

    def save(self, file_path: Path):
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(self.to_json(), f, indent=2)

    @classmethod
    def load(cls, file_path: Path) -> "ExternalDatasetManifest":
        if not file_path.is_file():
            return cls([])
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        records = [ExternalManifestRecord(**item) for item in data]
        return cls(records)
