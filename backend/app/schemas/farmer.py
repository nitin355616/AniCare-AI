from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class FarmerActionStep(BaseModel):
    step_number: int
    title_en: str
    title_hi: str
    description_en: str
    description_hi: str
    urgency: str = Field(default="routine", description="routine | important | critical")

class FarmerMedicine(BaseModel):
    name: str
    dosage: str
    frequency: str
    duration_days: int
    instructions: Optional[str] = None

class FarmerTreatmentPlan(BaseModel):
    is_active: bool = False
    approved_by_vet: Optional[str] = None
    vet_license_no: Optional[str] = None
    medicines: List[FarmerMedicine] = []
    instructions: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    doctor_approved_notice_en: str = "This medicine plan was approved by a certified veterinary doctor. AI does not prescribe medicine."
    doctor_approved_notice_hi: str = "यह दवा योजना प्रमाणित पशु चिकित्सक द्वारा स्वीकृत है। एआई दवाएं निर्धारित नहीं करता है।"

class FarmerWithdrawalNotice(BaseModel):
    is_active: bool = False
    restriction_type: str = "NONE"  # MILK_AND_MEAT | MILK_ONLY | MEAT_ONLY | NONE
    days_remaining: int = 0
    end_date: Optional[str] = None
    warning_message_en: str
    warning_message_hi: str

class FarmerVaccinationNotice(BaseModel):
    vaccine_name: Optional[str] = None
    target_disease: Optional[str] = None
    due_date: Optional[str] = None
    is_overdue: bool = False
    status: str = "NOT_SCHEDULED"

class FarmerFollowUpNotice(BaseModel):
    scheduled_date: Optional[str] = None
    is_overdue: bool = False
    vet_name: Optional[str] = None

class FarmerAnimalSummary(BaseModel):
    animal_id: str
    tag: str
    name: str
    species: str
    breed: Optional[str] = None
    age: Optional[str] = None
    weight: Optional[str] = None
    photo: Optional[str] = None
    health_status: str
    risk_level: str
    simplified_status: str  # HEALTHY | ATTENTION | URGENT
    status_label_en: str
    status_label_hi: str
    explanation_en: str
    explanation_hi: str
    action_needed: bool = False
    review_status: str = "NONE"  # NONE | PENDING | REVIEWED | IN_TREATMENT
    has_active_withdrawal: bool = False
    has_overdue_vaccine: bool = False

class FarmerAnimalDetail(FarmerAnimalSummary):
    action_steps: List[FarmerActionStep] = []
    vet_assigned_name: Optional[str] = None
    vet_helpline: Optional[str] = "+91 1800 233 0000"
    treatment_plan: Optional[FarmerTreatmentPlan] = None
    withdrawal_notice: Optional[FarmerWithdrawalNotice] = None
    vaccination_notice: Optional[FarmerVaccinationNotice] = None
    follow_up_notice: Optional[FarmerFollowUpNotice] = None
    recent_symptoms: List[str] = []
    last_checked_date: Optional[str] = None

class FarmerOutbreakWarning(BaseModel):
    has_warning: bool = False
    severity: str = "NORMAL"  # NORMAL | ELEVATED | HIGH
    title_en: str
    title_hi: str
    message_en: str
    message_hi: str
    action_en: str
    action_hi: str
    zone_name: str = "Anand District, Gujarat"

class FarmerDashboardResponse(BaseModel):
    farmer_name: str
    farmer_location: str
    total_animals: int
    healthy_count: int
    attention_count: int
    urgent_count: int
    outbreak_warning: FarmerOutbreakWarning
    animals: List[FarmerAnimalSummary]

class FarmerReviewRequest(BaseModel):
    symptoms: Optional[List[str]] = None
    notes: Optional[str] = None
    preferred_time: Optional[str] = None

class FarmerReviewResponse(BaseModel):
    success: bool
    case_id: str
    message_en: str
    message_hi: str
    requested_at: str
