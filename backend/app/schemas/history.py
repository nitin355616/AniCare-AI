from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class AssessmentHistoryItem(BaseModel):
    assessment_id: str
    animal_id: Optional[str] = None
    species: Optional[str] = "Cattle (Bovine)"
    possible_condition: str
    risk_level: str
    confidence: float
    explanation: Optional[str] = ""
    symptoms_detected: List[str] = []
    recommended_immediate_actions: List[str] = []
    veterinary_review_required: bool = True
    image_url: Optional[str] = None
    created_at: str
    source: Optional[str] = "ai_model"

class AssessmentHistoryResponse(BaseModel):
    total: int
    items: List[AssessmentHistoryItem]
    page: int = 1
    limit: int = 50
