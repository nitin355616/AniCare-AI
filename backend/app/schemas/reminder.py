from typing import Optional, List
from pydantic import BaseModel, Field

class ReminderCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=150, examples=["FMD Booster Vaccination"])
    description: Optional[str] = Field(default="", examples=["Administer second dose for cattle herd Shed 02"])
    animal_id: Optional[str] = Field(default=None, examples=["TAG-8821"])
    animal_tag: Optional[str] = Field(default=None, examples=["TAG-8821"])
    due_date: str = Field(..., examples=["2026-10-15"])
    reminder_type: str = Field(default="VACCINATION", examples=["VACCINATION", "VET_APPOINTMENT", "HEALTH_CHECK", "HYGIENE"])
    priority: str = Field(default="MEDIUM", examples=["HIGH", "MEDIUM", "LOW"])

class ReminderUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[str] = None
    status: Optional[str] = Field(None, examples=["PENDING", "COMPLETED"])
    priority: Optional[str] = None

class ReminderResponse(BaseModel):
    reminder_id: str
    title: str
    description: str = ""
    animal_id: Optional[str] = None
    animal_tag: Optional[str] = None
    due_date: str
    reminder_type: str
    priority: str
    status: str = "PENDING"
    created_at: str
    completed_at: Optional[str] = None

class ReminderListResponse(BaseModel):
    total: int
    items: List[ReminderResponse]
