from enum import Enum
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field

class CaseStatus(str, Enum):
    PENDING_REVIEW = "PENDING_REVIEW"
    REVIEWED = "REVIEWED"
    TREATMENT_ACTIVE = "TREATMENT_ACTIVE"
    FOLLOW_UP = "FOLLOW_UP"
    CLOSED = "CLOSED"

    @classmethod
    def normalize(cls, val: Optional[str]) -> str:
        if not val:
            return cls.PENDING_REVIEW.value
        clean = val.strip().upper().replace(" ", "_").replace("-", "_")
        if "PEND" in clean:
            return cls.PENDING_REVIEW.value
        if "REVIEW" in clean:
            return cls.REVIEWED.value
        if "TREAT" in clean or "CLINICAL" in clean:
            return cls.TREATMENT_ACTIVE.value
        if "FOLLOW" in clean:
            return cls.FOLLOW_UP.value
        if "CLOSE" in clean or "RESOLV" in clean:
            return cls.CLOSED.value
        return clean

class VetDecision(str, Enum):
    AI_ASSESSMENT_ACCEPTED = "AI_ASSESSMENT_ACCEPTED"
    AI_ASSESSMENT_MODIFIED = "AI_ASSESSMENT_MODIFIED"
    FURTHER_EXAMINATION_REQUIRED = "FURTHER_EXAMINATION_REQUIRED"
    URGENT_VETERINARY_ATTENTION = "URGENT_VETERINARY_ATTENTION"

class MedicineItem(BaseModel):
    medicine_name: str = Field(..., examples=["Flunixin Meglumine 50mg/mL"])
    formulation: Optional[str] = Field(default="Injectable Solution", examples=["Injectable Solution", "Bolus", "Oral Suspension", "Topical Ointment"])
    dosage: str = Field(..., examples=["15 mL IV once daily"])
    frequency: str = Field(default="Once daily", examples=["Once daily", "Twice daily"])
    duration: str = Field(..., examples=["3 days"])
    route: str = Field(default="Intravenous (IV)", examples=["Oral", "Intramuscular (IM)", "Intravenous (IV)", "Topical", "Subcutaneous (SC)"])
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    prescribing_vet: Optional[str] = None
    vet_license: Optional[str] = None
    instructions: Optional[str] = Field(default="", examples=["Administer slowly under sterile conditions."])

class TreatmentItem(BaseModel):
    """Backward-compatible treatment record."""
    treatment_id: Optional[str] = None
    medicine_name: str = Field(..., examples=["Flunixin Meglumine 50mg/mL"])
    dosage: str = Field(..., examples=["15 mL IV once daily"])
    duration: str = Field(..., examples=["3 days"])
    instructions: Optional[str] = Field(default="", examples=["Administer slowly via jugular vein."])
    prescribing_vet_license: str = Field(..., description="Certified veterinary medical license number is mandatory for prescriptions.", examples=["VET-REG-88402-GJ"])
    veterinary_approved: bool = Field(default=True, description="Indicates explicit signed approval by a licensed veterinary medical officer.")
    prescribed_at: Optional[str] = None

class AIAssessmentDetail(BaseModel):
    possible_condition: str = Field(..., examples=["Lumpy Skin Disease"])
    confidence: float = Field(..., examples=[88.5])
    risk_level: str = Field(..., examples=["HIGH"])
    explanation: Optional[str] = Field(default="", examples=["Circumscribed nodular lesions detected on cutaneous surface."])
    symptoms_detected: List[str] = Field(default_factory=list, examples=[["Cutaneous nodules", "Pyrexia"]])
    recommended_immediate_actions: List[str] = Field(default_factory=list, examples=[["Isolate animal", "Vector control"]])
    veterinary_review_required: bool = Field(default=True)

class VetReviewDetail(BaseModel):
    status: Optional[str] = Field(default="REVIEWED")
    vet_id: Optional[str] = Field(None, examples=["USR-VET-001"])
    vet_name: str = Field(..., examples=["Dr. Rajesh Patel"])
    vet_license_no: Optional[str] = Field(None, examples=["VET-REG-88402-GJ"])
    decision: str = Field(default=VetDecision.AI_ASSESSMENT_ACCEPTED.value, examples=["AI_ASSESSMENT_ACCEPTED"])
    clinical_notes: str = Field(default="", examples=["Physical examination confirms circumscribed nodular dermatitis."])
    veterinary_assessment: Optional[str] = Field(None, examples=["Confirmed Acute Bovine Lumpy Skin Disease"])
    reviewed_at: Optional[str] = None

class TreatmentPlanDetail(BaseModel):
    treatment_id: Optional[str] = None
    case_id: Optional[str] = None
    veterinary_assessment: Optional[str] = None
    diagnosis_assessment: str = Field(..., examples=["Confirmed Acute Bovine Lumpy Skin Disease"])
    medicines: List[MedicineItem] = Field(default_factory=list)
    supportive_care: Optional[str] = Field(default="", examples=["Fluid therapy and soft feed ration."])
    isolation_required: bool = Field(default=True)
    isolation_instructions: Optional[str] = Field(default="", examples=["Isolate in separate pen with vector fly-nets."])
    vaccination_advice: Optional[str] = Field(default="", examples=["Ring vaccination recommended for 5km cohort radius."])
    prevention_advice: Optional[str] = Field(default="", examples=["Mosquito netting and vector control."])
    instructions: Optional[str] = Field(default="", examples=["Strict quarantine in Pen 4."])
    farmer_instructions: Optional[str] = Field(default="", examples=["Keep the animal hydrated, do not alter prescribed dosage."])
    prescribed_by: Optional[str] = Field(None, examples=["Dr. Rajesh Patel"])
    prescription_license: Optional[str] = Field(None, examples=["VET-REG-88402-GJ"])
    treatment_start_date: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class PreventionPlanDetail(BaseModel):
    isolation_required: bool = Field(default=True)
    isolation_duration_days: Optional[int] = Field(default=14, examples=[14])
    isolation_instructions: Optional[str] = Field(default="", examples=["Separate pen with mosquito mesh netting."])
    hygiene_guidance: Optional[str] = Field(default="", examples=["Clean and disinfect water troughs and feeding equipment daily."])
    vector_control: Optional[str] = Field(default="", examples=["Apply bio-pesticide fly repellent spray and eliminate standing puddles."])
    animal_separation: Optional[str] = Field(default="", examples=["Segregate from milking herd cohorts and calves."])
    monitoring_protocol: Optional[str] = Field(default="", examples=["Check rectal temperature 2x daily; monitor rumination."])
    farmer_instructions: Optional[str] = Field(default="", examples=["Observe daily feed intake and report any fresh skin eruptions."])
    updated_at: Optional[str] = None

class WithdrawalDetail(BaseModel):
    withdrawal_type: str = Field(default="none", examples=["milk", "meat", "both", "none"])
    withdrawal_days: int = Field(default=0, ge=0, examples=[5])
    withdrawal_start_date: Optional[str] = None
    withdrawal_end_date: Optional[str] = None
    source: Optional[str] = Field(None, examples=["Manufacturer Product Label / Statutory Veterinary Formulary"])
    verified: bool = Field(default=False)
    status: str = Field(default="VERIFY_WITH_VETERINARIAN", examples=["ACTIVE", "COMPLETED", "VERIFY_WITH_VETERINARIAN", "NO_RESTRICTION"])
    days_remaining: Optional[int] = None
    safety_notice: Optional[str] = Field(default="Withdrawal period information is unavailable. Consult the prescribing veterinarian and applicable veterinary/food-safety guidance before using milk or meat products.")

class VaccinationRecord(BaseModel):
    vaccination_id: str = Field(..., examples=["VAC-2026-9041"])
    animal_id: str = Field(..., examples=["AN-GJ-2024-0104"])
    case_id: Optional[str] = None
    vaccine_name: str = Field(..., examples=["Goat Pox Vaccine (Killed)"])
    disease_target: str = Field(..., examples=["Lumpy Skin Disease"])
    date_administered: str = Field(..., examples=["2026-10-08"])
    next_due_date: str = Field(..., examples=["2027-10-08"])
    batch_number: Optional[str] = Field(default="", examples=["BATCH-LSD-2026-09"])
    administered_by: Optional[str] = Field(default="Dr. Rajesh Patel", examples=["Dr. Rajesh Patel"])
    notes: Optional[str] = Field(default="", examples=["Deep subcutaneous injection, left neck fold."])
    status: Optional[str] = Field(default="Completed", examples=["Completed", "Upcoming", "Overdue"])
    created_at: Optional[str] = None

class FollowUpDetail(BaseModel):
    required: bool = Field(default=True)
    follow_up_date: Optional[str] = Field(None, examples=["2026-10-12"])
    notes: Optional[str] = Field(default="", examples=["Re-evaluate lesion resolution and temperature."])
    completed: bool = Field(default=False)

class AuditTrailItem(BaseModel):
    action: str = Field(..., examples=["CASE_CREATED", "CASE_REVIEWED", "TREATMENT_CREATED", "PREVENTION_PLAN_UPDATED", "WITHDRAWAL_PERIOD_UPDATED", "VACCINATION_RECORDED", "FOLLOW_UP_SCHEDULED", "CASE_CLOSED"])
    user_id: Optional[str] = Field(None, examples=["USR-VET-001"])
    user_role: Optional[str] = Field(None, examples=["veterinarian"])
    details: Optional[str] = Field(default="")
    timestamp: str

class CaseCreateRequest(BaseModel):
    animal_id: str = Field(..., examples=["AN-GJ-2024-0104"])
    animal_name: Optional[str] = Field(default="Livestock Patient", examples=["Ganga"])
    animal_tag: Optional[str] = Field(None, examples=["TAG-8821"])
    species: str = Field(default="Cattle", examples=["Cattle"])
    owner_name: Optional[str] = Field(default="Local Livestock Farmer", examples=["Ramesh Patel"])
    location: Optional[str] = Field(default="Shed 04 - Bay A", examples=["Shed 04 - Bay A"])
    risk_level: str = Field(default="HIGH", examples=["HIGH", "CRITICAL", "MODERATE", "LOW"])
    ai_assessment: Optional[Union[AIAssessmentDetail, Dict[str, Any], str]] = None
    symptoms: Optional[List[str]] = Field(default_factory=list)
    clinical_observations: Optional[str] = None
    condition: Optional[str] = Field(default=None, examples=["Suspected Lumpy Skin Disease"])


class CaseReviewRequest(BaseModel):
    decision: Optional[str] = Field(default=VetDecision.AI_ASSESSMENT_ACCEPTED.value, examples=["AI_ASSESSMENT_ACCEPTED"])
    clinical_notes: Optional[str] = Field(default=None, examples=["Physical examination confirms nodular eruptions."])
    veterinary_assessment: Optional[str] = Field(default=None, examples=["Confirmed Lumpy Skin Disease"])
    # Backward compatibility with existing requests
    vet_name: Optional[str] = Field(default=None, examples=["Dr. Rajesh Patel"])
    vet_license_no: Optional[str] = Field(default=None, examples=["VET-REG-88402-GJ"])
    final_diagnosis: Optional[str] = Field(default=None, examples=["Confirmed Foot and Mouth Disease"])
    review_notes: Optional[str] = Field(default=None, examples=["Physical examination notes."])
    case_status: Optional[str] = Field(default=None, examples=["REVIEWED"])
    follow_up_date: Optional[str] = Field(default=None, examples=["2026-10-10"])

class CaseTreatmentRequest(BaseModel):
    diagnosis_assessment: Optional[str] = Field(default=None, examples=["Confirmed Lumpy Skin Disease"])
    medicines: Optional[List[MedicineItem]] = Field(default_factory=list)
    supportive_care: Optional[str] = Field(default="", examples=["Supportive antipyretic therapy."])
    isolation_required: Optional[bool] = Field(default=True)
    isolation_instructions: Optional[str] = Field(default="", examples=["Vector mesh netting pen."])
    vaccination_advice: Optional[str] = Field(default="", examples=["Vaccinate cohort."])
    prevention_advice: Optional[str] = Field(default="", examples=["Disinfect premises."])
    instructions: Optional[str] = Field(default="", examples=["Administer with clean water."])
    farmer_instructions: Optional[str] = Field(default="", examples=["Keep clean water available, follow dose."])
    prescribing_vet_license: Optional[str] = Field(default=None, examples=["VET-REG-88402-GJ"])
    # Optional integrated withdrawal input
    withdrawal_type: Optional[str] = Field(default=None, examples=["milk", "meat", "both", "none"])
    withdrawal_days: Optional[int] = Field(default=None, ge=0, examples=[5])
    withdrawal_source: Optional[str] = None
    withdrawal_verified: Optional[bool] = None
    # Backward compatibility fields for single medicine
    medicine_name: Optional[str] = Field(default=None, examples=["Flunixin Meglumine 50mg/mL"])
    dosage: Optional[str] = Field(default=None, examples=["15 mL IV once daily"])
    duration: Optional[str] = Field(default=None, examples=["3 days"])
    attending_vet_name: Optional[str] = Field(default=None, examples=["Dr. Rajesh Patel"])

class CasePreventionRequest(BaseModel):
    isolation_required: Optional[bool] = None
    isolation_duration_days: Optional[int] = Field(None, ge=0)
    isolation_instructions: Optional[str] = None
    hygiene_guidance: Optional[str] = None
    vector_control: Optional[str] = None
    animal_separation: Optional[str] = None
    monitoring_protocol: Optional[str] = None
    farmer_instructions: Optional[str] = None

class CaseWithdrawalRequest(BaseModel):
    withdrawal_type: str = Field(..., examples=["milk", "meat", "both", "none"])
    withdrawal_days: int = Field(..., description="Withdrawal days cannot be negative", examples=[7])
    withdrawal_start_date: Optional[str] = None
    source: Optional[str] = None
    verified: bool = False

class VaccinationCreateRequest(BaseModel):
    vaccine_name: str = Field(..., examples=["Goat Pox Vaccine (Killed)"])
    disease_target: str = Field(..., examples=["Lumpy Skin Disease"])
    date_administered: str = Field(..., examples=["2026-10-08"])
    next_due_date: str = Field(..., examples=["2027-10-08"])
    batch_number: Optional[str] = Field(default="", examples=["BATCH-LSD-2026-09"])
    administered_by: Optional[str] = Field(default="", examples=["Dr. Rajesh Patel"])
    case_id: Optional[str] = None
    notes: Optional[str] = Field(default="", examples=["Subcutaneous injection, lateral neck fold."])

class VaccinationUpdateRequest(BaseModel):
    vaccine_name: Optional[str] = None
    disease_target: Optional[str] = None
    date_administered: Optional[str] = None
    next_due_date: Optional[str] = None
    batch_number: Optional[str] = None
    administered_by: Optional[str] = None
    notes: Optional[str] = None

class CaseFollowUpRequest(BaseModel):
    required: bool = Field(default=True)
    follow_up_date: str = Field(..., examples=["2026-10-15"])
    notes: Optional[str] = Field(default="", examples=["Inspect nodule drying and appetite recovery."])

class CaseCloseRequest(BaseModel):
    notes: Optional[str] = Field(default="", examples=["Full recovery documented. Case resolved."])

class VeterinaryStatsResponse(BaseModel):
    pending_reviews: int = 0
    high_critical_cases: int = 0
    active_treatments: int = 0
    follow_ups_due: int = 0
    closed_cases: int = 0
    total_cases: int = 0
    vaccinations_due: int = 0
    withdrawal_restrictions: int = 0

class VeterinaryCaseResponse(BaseModel):
    case_id: str
    animal_id: str
    animal_tag: Optional[str] = None
    animal_name: str
    species: str
    owner_name: Optional[str] = "Registered Farmer"
    location: Optional[str] = "Shed 01"
    risk_level: str = "MODERATE"
    ai_assessment: Union[AIAssessmentDetail, str]
    ai_confidence: Optional[float] = None
    attending_vet: Optional[str] = None
    vet_review: Optional[Union[VetReviewDetail, str]] = None
    final_diagnosis: Optional[str] = None
    treatment_plan: Optional[TreatmentPlanDetail] = None
    treatments: List[TreatmentItem] = []
    prevention_plan: Optional[PreventionPlanDetail] = None
    withdrawal_information: Optional[WithdrawalDetail] = None
    vaccination_record: Optional[VaccinationRecord] = None
    follow_up: Optional[FollowUpDetail] = None
    follow_up_date: Optional[str] = None
    case_status: str = CaseStatus.PENDING_REVIEW.value
    audit_trail: List[AuditTrailItem] = []
    created_at: str
    updated_at: str
