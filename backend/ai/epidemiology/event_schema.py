"""
AniCare AI — Outbreak & Epidemiology Event Schema
Defines the standardized epidemiological reporting data contract for early-warning
disease surveillance, integrating AI detections, farmer alerts, field vet diagnoses,
and official Department of Animal Husbandry & Dairying (DAHD) records.
"""

from enum import Enum
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, field_validator, model_validator
import re
from datetime import datetime

try:
    from ai.dataset.schema import TargetSpeciesEnum
except ImportError:
    from backend.ai.dataset.schema import TargetSpeciesEnum


class VaccinationStatusEnum(str, Enum):
    VACCINATED = "VACCINATED"
    UNVACCINATED = "UNVACCINATED"
    PARTIALLY_VACCINATED = "PARTIALLY_VACCINATED"
    UNKNOWN = "UNKNOWN"


class EventSourceEnum(str, Enum):
    AI_VISUAL_DETECTION = "AI_VISUAL_DETECTION"
    FARMER_SYMPTOM_REPORT = "FARMER_SYMPTOM_REPORT"
    VETERINARY_CLINICAL_DIAGNOSIS = "VETERINARY_CLINICAL_DIAGNOSIS"
    OFFICIAL_DAHD_NOTIFICATION = "OFFICIAL_DAHD_NOTIFICATION"


class VerificationStatusEnum(str, Enum):
    UNVERIFIED = "UNVERIFIED"
    FIELD_INVESTIGATION_PENDING = "FIELD_INVESTIGATION_PENDING"
    LAB_CONFIRMED = "LAB_CONFIRMED"
    FALSE_POSITIVE = "FALSE_POSITIVE"
    RESOLVED = "RESOLVED"


class GeoLocation(BaseModel):
    """Structured administrative and geographic coordinates for spatial clustering."""
    state: str = Field(..., examples=["Gujarat"])
    district: str = Field(..., examples=["Anand"])
    block_or_taluk: Optional[str] = Field(None, examples=["Petlad"])
    village_or_town: Optional[str] = Field(None, examples=["Boriavi"])
    latitude: Optional[float] = Field(None, ge=-90.0, le=90.0)
    longitude: Optional[float] = Field(None, ge=-180.0, le=180.0)


class EpidemiologyEvent(BaseModel):
    """
    Standardized event record for multi-source disease surveillance and cluster detection.
    """
    event_id: str = Field(..., examples=["EPI-GJ-2026-0042"])
    disease: str = Field(..., examples=["Foot and Mouth Disease"])
    species: TargetSpeciesEnum
    location: GeoLocation
    date: str = Field(..., description="Date of occurrence in YYYY-MM-DD format", examples=["2026-03-15"])
    affected_count: int = Field(default=0, ge=0, description="Total animals showing clinical symptoms")
    suspected_count: int = Field(default=0, ge=0, description="Animals at-risk or in close contact")
    confirmed_count: int = Field(default=0, ge=0, description="Laboratory or veterinary-verified cases")
    mortality_count: int = Field(default=0, ge=0, description="Animals succumbed to disease")
    vaccination_status: VaccinationStatusEnum = VaccinationStatusEnum.UNKNOWN
    source: EventSourceEnum
    verification_status: VerificationStatusEnum = VerificationStatusEnum.UNVERIFIED
    notes: Optional[str] = Field(default="", examples=["Sudden lameness and vesicles noted across 3 herds."])

    @field_validator("date", mode="after")
    @classmethod
    def validate_date_format(cls, v: str) -> str:
        """Enforces ISO YYYY-MM-DD date format."""
        try:
            datetime.strptime(v, "%Y-%m-%d")
        except ValueError:
            raise ValueError(f"Date '{v}' must strictly follow YYYY-MM-DD format.")
        return v

    @field_validator("notes", mode="after")
    @classmethod
    def sanitize_pii(cls, v: Optional[str]) -> str:
        """Sanitizes personal identifiable contact information (e.g. mobile numbers)."""
        if not v:
            return ""
        if re.search(r"\b[6-9]\d{9}\b", v):
            raise ValueError("PII Security Violation: Private telephone number detected in event notes.")
        return v

    @model_validator(mode="after")
    def validate_count_consistency(self) -> "EpidemiologyEvent":
        """Ensures logical mathematical consistency between epidemiological counts."""
        total_observed = self.affected_count + self.suspected_count
        if self.confirmed_count > total_observed and total_observed > 0:
            raise ValueError(
                f"Count inconsistency: Confirmed count ({self.confirmed_count}) exceeds total affected and suspected ({total_observed})."
            )
        if self.mortality_count > total_observed and total_observed > 0:
            raise ValueError(
                f"Count inconsistency: Mortality count ({self.mortality_count}) cannot exceed total recorded animals ({total_observed})."
            )
        return self
