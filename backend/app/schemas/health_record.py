from typing import Optional, List
from pydantic import BaseModel, Field

class HealthRecordCreate(BaseModel):
    animal_id: str = Field(..., examples=["AN-GJ-2024-0104"])
    symptoms: List[str] = Field(default_factory=list, examples=[["Fever", "Tachypnea"]])
    temperature: Optional[str] = Field(default="101.5 °F", examples=["104.8 °F"])
    appetite: Optional[str] = Field(default="Normal", examples=["Severely Reduced"])
    activity: Optional[str] = Field(default="Normal", examples=["Lethargic / Recumbent"])
    breathing: Optional[str] = Field(default="Normal", examples=["Rapid / Dyspneic"])
    observations: Optional[str] = Field(default="", examples=["Observed nasal discharge during morning rounds."])
    previous_conditions: Optional[List[str]] = Field(default_factory=list, examples=[["Mastitis treated Aug 2026"]])
    vaccination_status: Optional[str] = Field(default="Up to date", examples=["FMD Booster Active"])
    recorded_by: Optional[str] = Field(default="Field Officer", examples=["Dr. Arvind Verma"])

class HealthRecordResponse(BaseModel):
    id: str
    animal_id: str
    symptoms: List[str] = []
    temperature: Optional[str] = None
    appetite: Optional[str] = None
    activity: Optional[str] = None
    breathing: Optional[str] = None
    observations: Optional[str] = None
    previous_conditions: List[str] = []
    vaccination_status: Optional[str] = None
    recorded_by: Optional[str] = None
    timestamp: str

class HealthRecordListResponse(BaseModel):
    animal_id: str
    total: int
    records: List[HealthRecordResponse]
