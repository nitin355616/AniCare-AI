from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class ImageUploadResponse(BaseModel):
    image_id: str = Field(..., examples=["IMG-A1B2C3D4E5F6"])
    filename: str = Field(..., examples=["IMG-A1B2C3D4E5F6.jpg"])
    original_filename: str = Field(..., examples=["lesion_sample.jpg"])
    content_type: str = Field(..., examples=["image/jpeg"])
    file_size_bytes: int = Field(..., examples=[248102])
    url: str = Field(..., examples=["/uploads/IMG-A1B2C3D4E5F6.jpg"])
    created_at: str


class DetectionAnalyzeRequest(BaseModel):
    image_id: Optional[str] = Field(None, examples=["IMG-A1B2C3D4E5F6"])
    animal_id: Optional[str] = Field(None, examples=["AN-GJ-2024-0104"])
    species: Optional[str] = Field(default="Cattle", examples=["Cattle (Bovine)"])
    temperature: Optional[str] = Field(default="104.4 °F", examples=["104.4 °F"])
    appetite: Optional[str] = Field(default="Reduced", examples=["Severely Reduced"])
    activity_level: Optional[str] = Field(default="Lethargic", examples=["Lethargic / Dull"])
    breathing_condition: Optional[str] = Field(default="Rapid", examples=["Rapid / Dyspneic"])
    symptoms: List[str] = Field(
        default_factory=list,
        examples=[["Rapid, shallow dyspneic breathing", "Serous to mucopurulent nasal discharge", "Fever"]]
    )
    observations: Optional[str] = Field(
        default="",
        examples=["Audible grunting during expiration and refusal of dry fodder."]
    )

    # Multi-Modal Telemetry & Contextual Extensions (Milestone 6)
    heart_rate: Optional[float] = Field(None, examples=[72.0], description="Heart rate in beats per minute")
    respiratory_rate: Optional[float] = Field(None, examples=[32.0], description="Breaths per minute")
    vaccination_status: Optional[str] = Field(default="UNKNOWN", examples=["VACCINATED", "UNVACCINATED", "UNKNOWN"])
    age_months: Optional[int] = Field(None, examples=[36], description="Age in months")
    recent_nearby_cases: Optional[int] = Field(default=0, examples=[2], description="Active cases within 10km radius")
    herd_at_risk_count: Optional[int] = Field(default=0, examples=[1], description="Concurrent sick herd members")
    cluster_warning_active: Optional[bool] = Field(default=False, description="Whether an active cluster alert exists")
    recent_movement: Optional[bool] = Field(default=False, description="Recent transit/livestock market introduction")
    enable_tiled_inference: Optional[bool] = Field(default=False, description="Enable multi-crop tiled inference")
    request_explainability: Optional[bool] = Field(default=False, description="Generate Grad-CAM saliency overlay")


class DifferentialDiagnosisItem(BaseModel):
    disease: str
    probability: float
    rationale: str


class DetectionAnalyzeResponse(BaseModel):
    assessment_id: str
    is_demo_inference: bool = True
    model_version: str = "AniCare-Net v1.2-DemoEngine"
    possible_condition: str
    confidence: float
    risk_level: str  # "CRITICAL", "HIGH", "MODERATE", "LOW"
    risk_score: Optional[float] = None
    risk_reasoning: Optional[str] = None
    symptoms_detected: List[str]
    symptom_evidence: List[str] = []
    detected_visual_indicators: List[str] = []
    contributing_factors: List[str] = []
    explanation: str
    recommended_immediate_actions: List[str]
    veterinary_review_required: bool = True
    preventive_actions: List[str] = []
    differential_diagnoses: List[DifferentialDiagnosisItem] = []
    disclaimer: str
    created_at: str

    # Multi-Modal Scoring & Early-Warning Extensions (Milestone 6)
    visual_risk_score: Optional[float] = None
    symptom_risk_score: Optional[float] = None
    physiological_risk_score: Optional[float] = None
    epidemiological_risk_score: Optional[float] = None
    history_risk_score: Optional[float] = None
    overall_risk_score: Optional[float] = None
    model_scope: Optional[Dict[str, Any]] = None
    operating_threshold: Optional[float] = None
    explainability: Optional[Dict[str, Any]] = None
    early_warning_signal: Optional[Dict[str, Any]] = None
