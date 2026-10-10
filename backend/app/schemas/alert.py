from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field

class AlertTypeEnum(str, Enum):
    CRITICAL = "critical"
    DISEASE_RISK = "disease-risk"
    FOLLOW_UP = "follow-up"
    VACCINATION = "vaccination"
    PREVENTIVE = "preventive"

class AlertSeverityEnum(str, Enum):
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"

class AlertCreate(BaseModel):
    title: str = Field(..., examples=["Clustered LSD Outbreak Warning in Sector 04"])
    description: str = Field(..., examples=["ANI-NET spatial anomaly detected 7 high-probability Lumpy Skin cases within a 48h window."])
    alert_type: AlertTypeEnum = Field(default=AlertTypeEnum.CRITICAL)
    severity: AlertSeverityEnum = Field(default=AlertSeverityEnum.CRITICAL)
    location: str = Field(..., examples=["Anand District, Radius 12km"])
    affected_tag: Optional[str] = Field(None, examples=["TAG-7719 + 6 Cohorts"])
    animal_id: Optional[str] = Field(None, examples=["AN-GJ-2024-0412"])
    action_required: str = Field(..., examples=["Enact Ring Quarantine & Vector Fumigation"])
    dispatch_status: Optional[str] = Field(default="Vet Team Dispatched", examples=["Vet Team Dispatched"])

class AlertAcknowledgeRequest(BaseModel):
    acknowledged_by: Optional[str] = Field(default="Field Officer", examples=["Dr. Arvind Verma"])
    notes: Optional[str] = Field(default="", examples=["Incident verified on site. Protocols initiated."])

class AlertResponse(BaseModel):
    alert_id: str
    title: str
    description: str
    alert_type: str
    severity: str
    location: str
    affected_tag: Optional[str] = None
    animal_id: Optional[str] = None
    action_required: str
    dispatch_status: str
    status: str  # "Active", "Acknowledged", "Resolved"
    acknowledged_by: Optional[str] = None
    created_at: str
    acknowledged_at: Optional[str] = None

class AlertListResponse(BaseModel):
    total: int
    unacknowledged: int
    items: List[AlertResponse]
