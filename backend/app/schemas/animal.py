from typing import Optional, List
from pydantic import BaseModel, Field

class AnimalCreate(BaseModel):
    name: str = Field(..., examples=["Ganga"])
    tag: str = Field(..., examples=["TAG-8821"])
    species: str = Field(..., examples=["Cattle"])
    breed: Optional[str] = Field(default="Indigenous", examples=["Gir"])
    gender: Optional[str] = Field(default="Female", examples=["Female"])
    age: Optional[str] = Field(default="3.0 years", examples=["4.2 years"])
    weight: Optional[str] = Field(default="400 kg", examples=["440 kg"])
    owner: Optional[str] = Field(default="Amul Anand Dairy Co-op", examples=["Amul Anand Dairy Co-op"])
    photo: Optional[str] = Field(
        default="https://images.unsplash.com/photo-1546445317-29f4545e9d53?auto=format&fit=crop&w=400&q=80",
        examples=["https://images.unsplash.com/photo-1546445317-29f4545e9d53?auto=format&fit=crop&w=400&q=80"]
    )
    health_status: Optional[str] = Field(default="Healthy", examples=["Under Observation"])
    risk_level: Optional[str] = Field(default="Low", examples=["High Risk"])
    symptoms: Optional[List[str]] = Field(default_factory=list, examples=[["Fever", "Oral salivation"]])
    location: Optional[str] = Field(default="Shed 01", examples=["Shed 04 - Bay A"])
    notes: Optional[str] = Field(default="", examples=["Routine milking unit"])

class AnimalUpdate(BaseModel):
    name: Optional[str] = None
    tag: Optional[str] = None
    species: Optional[str] = None
    breed: Optional[str] = None
    gender: Optional[str] = None
    age: Optional[str] = None
    weight: Optional[str] = None
    owner: Optional[str] = None
    photo: Optional[str] = None
    health_status: Optional[str] = None
    risk_level: Optional[str] = None
    symptoms: Optional[List[str]] = None
    location: Optional[str] = None
    notes: Optional[str] = None

class AnimalResponse(BaseModel):
    animal_id: str
    name: str
    tag: str
    species: str
    breed: Optional[str] = None
    gender: Optional[str] = None
    age: Optional[str] = None
    weight: Optional[str] = None
    owner: Optional[str] = None
    photo: Optional[str] = None
    health_status: str
    risk_level: str
    symptoms: List[str] = []
    location: Optional[str] = None
    notes: Optional[str] = None
    created_at: str
    updated_at: str

class AnimalListResponse(BaseModel):
    total: int
    items: List[AnimalResponse]
