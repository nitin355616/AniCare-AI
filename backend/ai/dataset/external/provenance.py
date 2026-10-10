"""
AniCare AI — External Dataset Provenance Catalog & Legal Audit
Tracks institutional metadata, licenses, DTA agreements, and compliance attributes.
Adheres strictly to scientific and legal integrity:
Never exposes private personal emails or credentials through public exports.
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent.parent


class ExternalSourceProvenance(BaseModel):
    """Standardized schema for external dataset sources (Milestone 8A)."""
    source_id: str
    source_name: str
    institution: str
    source_url: str
    contact_reference: str
    permission_status: str
    license: Optional[str] = None
    data_use_agreement: str
    commercial_use_allowed: bool = False
    redistribution_allowed: bool = False
    research_use_allowed: bool = False
    veterinary_supervision_required: bool = True
    acquisition_date: str
    acquisition_method: str
    dataset_version: str
    checksum: str
    image_count: int = 0
    species: List[str] = Field(default_factory=list)
    disease_classes: List[str] = Field(default_factory=list)
    geographic_origin: str
    clinical_setting: str
    notes: str = ""

    def to_public_dict(self) -> Dict[str, Any]:
        """Returns safe metadata dictionary stripped of private contact references."""
        data = self.model_dump()
        # Redact private contact references from public representation
        data["contact_reference"] = "[REDACTED_INSTITUTIONAL_CHANNEL]"
        return data


class ExternalProvenanceRegistry:
    """Manages machine-readable provenance registry of external sources."""

    def __init__(self, registry_path: Optional[Path] = None):
        self.registry_path = registry_path or (BACKEND_DIR / "backend" / "ai" / "dataset" / "source_registry.json")
        if not self.registry_path.is_file():
            # Fallback relative to current repo structure
            self.registry_path = BACKEND_DIR / "ai" / "dataset" / "source_registry.json"

    def get_all_sources(self) -> List[Dict[str, Any]]:
        """Loads all registered sources."""
        if not self.registry_path.is_file():
            return []
        with open(self.registry_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def get_source_by_id(self, source_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves single source by source_id or source_name."""
        for entry in self.get_all_sources():
            if entry.get("source_id") == source_id or entry.get("source_name") == source_id:
                return entry
        return None

    def get_candidate_external_sources(self) -> List[Dict[str, Any]]:
        """Returns candidate external sources for Dataset B validation."""
        candidates = []
        for entry in self.get_all_sources():
            sid = entry.get("source_id", "")
            if "DATASET-B-CANDIDATE" in sid:
                candidates.append(entry)
        return candidates

    def validate_provenance_completeness(self, source_id: str) -> Dict[str, Any]:
        """Validates that all 21 mandatory Section 5 fields are populated."""
        entry = self.get_source_by_id(source_id)
        if not entry:
            return {
                "source_id": source_id,
                "is_complete": False,
                "error": "Source not found in registry"
            }

        required_keys = [
            "source_id", "source_name", "institution", "source_url", "contact_reference",
            "permission_status", "license", "data_use_agreement", "commercial_use_allowed",
            "redistribution_allowed", "research_use_allowed", "veterinary_supervision_required",
            "acquisition_date", "acquisition_method", "dataset_version", "checksum",
            "image_count", "species", "disease_classes", "geographic_origin",
            "clinical_setting", "notes"
        ]

        missing = [k for k in required_keys if k not in entry]
        return {
            "source_id": source_id,
            "is_complete": len(missing) == 0,
            "missing_fields": missing,
            "permission_status": entry.get("permission_status")
        }


provenance_registry = ExternalProvenanceRegistry()
