import datetime
import uuid
import re
from typing import List, Optional, Dict, Any
from fastapi import HTTPException, status
from app.database import (
    get_veterinary_cases_collection,
    get_vaccinations_collection,
    get_animals_collection,
    get_alerts_collection
)
from app.schemas.veterinary import (
    VeterinaryCaseResponse,
    CaseStatus,
    VetDecision,
    AIAssessmentDetail,
    VetReviewDetail,
    TreatmentPlanDetail,
    FollowUpDetail,
    AuditTrailItem,
    MedicineItem,
    TreatmentItem,
    CaseCreateRequest,
    CaseReviewRequest,
    CaseTreatmentRequest,
    CaseFollowUpRequest,
    CaseCloseRequest,
    VeterinaryStatsResponse,
    PreventionPlanDetail,
    WithdrawalDetail,
    VaccinationRecord,
    CasePreventionRequest,
    CaseWithdrawalRequest,
    VaccinationCreateRequest,
    VaccinationUpdateRequest
)

DEFAULT_DEMO_CASES = [
    {
        "case_id": "CASE-2026-041",
        "animal_id": "AN-GJ-2024-0104",
        "animal_tag": "TAG-8821",
        "animal_name": "Ganga",
        "species": "Cattle (Gir)",
        "owner_name": "Kishorbhai Patel",
        "location": "Shed 04 - Bay A",
        "risk_level": "CRITICAL",
        "ai_assessment": {
            "possible_condition": "Lumpy Skin Disease",
            "confidence": 94.6,
            "risk_level": "CRITICAL",
            "explanation": "Multiple raised circumscribed cutaneous nodules across dewlap and cervical region with pyrexia.",
            "symptoms_detected": ["Cutaneous nodules", "Pyrexia (104.8°F)", "Enlarged prescapular lymph nodes"],
            "recommended_immediate_actions": [
                "Strict physical isolation in vector-proof pen",
                "Immediate veterinary officer clinical review",
                "Install insect-proof netting around enclosure"
            ],
            "veterinary_review_required": True
        },
        "ai_confidence": 94.6,
        "attending_vet": None,
        "vet_review": None,
        "final_diagnosis": None,
        "treatment_plan": None,
        "treatments": [],
        "follow_up": None,
        "follow_up_date": None,
        "case_status": "PENDING_REVIEW",
        "audit_trail": [
            {
                "action": "CASE_CREATED",
                "user_id": "USR-SYSTEM-AI",
                "user_role": "system",
                "details": "Automated case created following CRITICAL visual lesion detection.",
                "timestamp": "2026-10-06T08:15:00Z"
            }
        ]
    },
    {
        "case_id": "CASE-2026-042",
        "animal_id": "AN-GJ-2024-0412",
        "animal_tag": "TAG-7719",
        "animal_name": "Nandi",
        "species": "Cattle (Kankrej)",
        "owner_name": "Sureshbhai Desai",
        "location": "Shed 06 - Enclosure",
        "risk_level": "HIGH",
        "ai_assessment": {
            "possible_condition": "Lumpy Skin Disease",
            "confidence": 91.2,
            "risk_level": "HIGH",
            "explanation": "Circumscribed nodular eruptions on neck and shoulder. Lesions match stage 2 capripox dermatitis.",
            "symptoms_detected": ["Circumscribed nodules", "Mild salivation", "Lethargy"],
            "recommended_immediate_actions": [
                "Isolate animal from milking herd",
                "Supportive anti-inflammatory cover"
            ],
            "veterinary_review_required": True
        },
        "ai_confidence": 91.2,
        "attending_vet": "Dr. Rajesh Patel",
        "vet_review": {
            "status": "REVIEWED",
            "vet_id": "USR-VET-001",
            "vet_name": "Dr. Rajesh Patel",
            "vet_license_no": "VET-REG-88402-GJ",
            "decision": "AI_ASSESSMENT_ACCEPTED",
            "clinical_notes": "Physical palpation confirms firm circumscribed dermal nodules (2-4cm). Pre-scapular lymphadenopathy noted.",
            "veterinary_assessment": "Confirmed Acute Bovine Lumpy Skin Disease (Capripox)",
            "reviewed_at": "2026-10-06T11:00:00Z"
        },
        "final_diagnosis": "Confirmed Acute Bovine Lumpy Skin Disease (Capripox)",
        "treatment_plan": None,
        "treatments": [],
        "follow_up": None,
        "follow_up_date": None,
        "case_status": "REVIEWED",
        "audit_trail": [
            {
                "action": "CASE_CREATED",
                "user_id": "USR-SYSTEM-AI",
                "user_role": "system",
                "details": "Case created from HIGH risk early warning signal.",
                "timestamp": "2026-10-06T09:30:00Z"
            },
            {
                "action": "CASE_REVIEWED",
                "user_id": "USR-VET-001",
                "user_role": "veterinarian",
                "details": "AI Assessment Accepted by Dr. Rajesh Patel (VET-REG-88402-GJ).",
                "timestamp": "2026-10-06T11:00:00Z"
            }
        ]
    },
    {
        "case_id": "CASE-2026-043",
        "animal_id": "AN-PB-2024-0210",
        "animal_tag": "TAG-9901",
        "animal_name": "Bhim",
        "species": "Buffalo (Murrah)",
        "owner_name": "Harpreet Singh",
        "location": "Shed 09 - Testing Bay",
        "risk_level": "HIGH",
        "ai_assessment": {
            "possible_condition": "Bovine Respiratory Disease (BRD)",
            "confidence": 88.0,
            "risk_level": "HIGH",
            "explanation": "Dyspneic breathing pattern, bilateral mucopurulent nasal discharge, and reduced feed intake.",
            "symptoms_detected": ["Dyspnea", "Nasal catarrh", "Fever (103.9°F)"],
            "recommended_immediate_actions": [
                "Thoracic auscultation",
                "Broad-spectrum antibiotic cover",
                "Isolate in warm, ventilated bay"
            ],
            "veterinary_review_required": True
        },
        "ai_confidence": 88.0,
        "attending_vet": "Dr. Ananya Sharma",
        "vet_review": {
            "status": "REVIEWED",
            "vet_id": "USR-VET-002",
            "vet_name": "Dr. Ananya Sharma",
            "vet_license_no": "VET-REG-91044-GJ",
            "decision": "AI_ASSESSMENT_ACCEPTED",
            "clinical_notes": "Auscultation confirms dry rales in cranial lung fields. Respiratory distress verified.",
            "veterinary_assessment": "Bovine Respiratory Disease Complex (Bacterial Secondary Infiltration)",
            "reviewed_at": "2026-10-06T14:00:00Z"
        },
        "final_diagnosis": "Bovine Respiratory Disease Complex (Bacterial Secondary Infiltration)",
        "treatment_plan": {
            "diagnosis_assessment": "Bovine Respiratory Disease Complex",
            "medicines": [
                {
                    "medicine_name": "Florfenicol 300mg/mL",
                    "dosage": "20 mg/kg IM (40 mL total)",
                    "frequency": "Once every 48 hours",
                    "duration": "4 days (2 doses)",
                    "route": "Intramuscular (IM)",
                    "instructions": "Administer into anterior neck musculature under aseptic precautions."
                },
                {
                    "medicine_name": "Flunixin Meglumine 50mg/mL",
                    "dosage": "2.2 mg/kg IV (20 mL total)",
                    "frequency": "Once daily",
                    "duration": "3 days",
                    "route": "Intravenous (IV)",
                    "instructions": "Slow jugular intravenous injection."
                }
            ],
            "supportive_care": "Warm dry bedding, steam nebulization with eucalyptus oil, electrolyte fluids.",
            "isolation_required": True,
            "vaccination_advice": "Administer polyvalent respiratory bacterin after acute convalescence.",
            "prevention_advice": "Improve shed air exchange and eliminate damp bedding.",
            "instructions": "Monitor rectal temperature twice daily. Keep in isolation.",
            "prescribed_by": "Dr. Ananya Sharma",
            "prescription_license": "VET-REG-91044-GJ",
            "treatment_start_date": "2026-10-06"
        },
        "treatments": [
            {
                "treatment_id": "TRT-001",
                "medicine_name": "Florfenicol 300mg/mL",
                "dosage": "20 mg/kg IM (40 mL total)",
                "duration": "4 days",
                "instructions": "Administer into neck muscle.",
                "prescribing_vet_license": "VET-REG-91044-GJ",
                "veterinary_approved": True,
                "prescribed_at": "2026-10-06T14:30:00Z"
            }
        ],
        "follow_up": None,
        "follow_up_date": None,
        "case_status": "TREATMENT_ACTIVE",
        "audit_trail": [
            {
                "action": "CASE_CREATED",
                "user_id": "USR-SYSTEM-AI",
                "user_role": "system",
                "details": "Case created from respiratory telemetry.",
                "timestamp": "2026-10-06T12:00:00Z"
            },
            {
                "action": "CASE_REVIEWED",
                "user_id": "USR-VET-002",
                "user_role": "veterinarian",
                "details": "Clinical examination confirmed BRD.",
                "timestamp": "2026-10-06T14:00:00Z"
            },
            {
                "action": "TREATMENT_CREATED",
                "user_id": "USR-VET-002",
                "user_role": "veterinarian",
                "details": "Prescribed Florfenicol + Flunixin Meglumine regimen.",
                "timestamp": "2026-10-06T14:30:00Z"
            }
        ]
    },
    {
        "case_id": "CASE-2026-044",
        "animal_id": "AN-GJ-2024-0305",
        "animal_tag": "TAG-6119",
        "animal_name": "Surabhi",
        "species": "Cattle (Jersey Cross)",
        "owner_name": "Dineshbhai Rabari",
        "location": "Shed 02 - Milking Parlor",
        "risk_level": "MODERATE",
        "ai_assessment": {
            "possible_condition": "Bovine Mastitis (Subclinical to Clinical)",
            "confidence": 84.5,
            "risk_level": "MODERATE",
            "explanation": "Right rear quarter inflammation with electrical conductivity elevation in milk.",
            "symptoms_detected": ["Quarter swelling", "Flakes in foremilk"],
            "recommended_immediate_actions": ["California Mastitis Test (CMT)", "Intramammary antibiotic infusion"],
            "veterinary_review_required": True
        },
        "ai_confidence": 84.5,
        "attending_vet": "Dr. Rajesh Patel",
        "vet_review": {
            "status": "REVIEWED",
            "vet_id": "USR-VET-001",
            "vet_name": "Dr. Rajesh Patel",
            "vet_license_no": "VET-REG-88402-GJ",
            "decision": "AI_ASSESSMENT_ACCEPTED",
            "clinical_notes": "CMT 3+ reaction in right hind quarter. Foremilk shows purulent curdling.",
            "veterinary_assessment": "Clinical Streptococcal Mastitis (Right Hind Quarter)",
            "reviewed_at": "2026-10-05T09:00:00Z"
        },
        "final_diagnosis": "Clinical Streptococcal Mastitis (Right Hind Quarter)",
        "treatment_plan": {
            "diagnosis_assessment": "Clinical Streptococcal Mastitis",
            "medicines": [
                {
                    "medicine_name": "Cloxacillin Intramammary Infusion 200mg",
                    "dosage": "1 syringe per affected quarter",
                    "frequency": "Every 12 hours after complete stripping",
                    "duration": "3 days (6 infusions)",
                    "route": "Intramammary",
                    "instructions": "Teat dip with 1% povidone iodine before and after infusion."
                }
            ],
            "supportive_care": "Frequent milking out of affected quarter (4 times daily), cold water hosing.",
            "isolation_required": False,
            "vaccination_advice": "Maintain strict post-milking teat dipping.",
            "prevention_advice": "Disinfect milking clusters between cows.",
            "instructions": "Discard milk from treated cow during 7-day milk withholding period.",
            "prescribed_by": "Dr. Rajesh Patel",
            "prescription_license": "VET-REG-88402-GJ",
            "treatment_start_date": "2026-10-05"
        },
        "treatments": [],
        "follow_up": {
            "required": True,
            "follow_up_date": "2026-10-10",
            "notes": "Perform repeat CMT strip test to verify somatic cell count normalization.",
            "completed": False
        },
        "follow_up_date": "2026-10-10",
        "case_status": "FOLLOW_UP",
        "audit_trail": [
            {
                "action": "CASE_CREATED",
                "user_id": "USR-SYSTEM-AI",
                "user_role": "system",
                "details": "Case created from automated milking telemetry.",
                "timestamp": "2026-10-05T08:00:00Z"
            },
            {
                "action": "CASE_REVIEWED",
                "user_id": "USR-VET-001",
                "user_role": "veterinarian",
                "details": "CMT test confirmed right hind mastitis.",
                "timestamp": "2026-10-05T09:00:00Z"
            },
            {
                "action": "TREATMENT_CREATED",
                "user_id": "USR-VET-001",
                "user_role": "veterinarian",
                "details": "Prescribed intramammary Cloxacillin therapy.",
                "timestamp": "2026-10-05T09:30:00Z"
            },
            {
                "action": "FOLLOW_UP_SCHEDULED",
                "user_id": "USR-VET-001",
                "user_role": "veterinarian",
                "details": "Scheduled CMT verification follow-up for 2026-10-10.",
                "timestamp": "2026-10-05T10:00:00Z"
            }
        ]
    }
]

def _format_case_doc(doc: Dict[str, Any]) -> VeterinaryCaseResponse:
    doc.pop("_id", None)
    if not doc.get("case_status"):
        doc["case_status"] = doc.get("status", CaseStatus.PENDING_REVIEW.value)
    if "owner_name" not in doc:
        doc["owner_name"] = "Registered Dairy Cooperative Member"
    if "location" not in doc:
        doc["location"] = "Shed 01"
    if "audit_trail" not in doc:
        doc["audit_trail"] = []
    if "ai_assessment" not in doc or not doc["ai_assessment"]:
        doc["ai_assessment"] = {
            "possible_condition": doc.get("condition", "Suspected Lumpy Skin Disease"),
            "confidence": 85.0,
            "risk_level": doc.get("risk_level", "HIGH"),
            "veterinary_review_required": True,
            "symptoms_detected": ["Cutaneous nodules", "Pyrexia"]
        }
    return VeterinaryCaseResponse(**doc)


async def seed_default_cases_if_empty() -> None:
    col = get_veterinary_cases_collection()
    if col is None:
        return
    count = await col.count_documents({})
    if count == 0:
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
        docs = []
        for c in DEFAULT_DEMO_CASES:
            doc = c.copy()
            doc["created_at"] = now_iso
            doc["updated_at"] = now_iso
            docs.append(doc)
        await col.insert_many(docs)

async def get_veterinary_cases(
    status_filter: Optional[str] = None,
    risk_filter: Optional[str] = None,
    animal_id: Optional[str] = None,
    limit: int = 50,
    skip: int = 0
) -> List[VeterinaryCaseResponse]:
    col = get_veterinary_cases_collection()
    if col is None:
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
        res = []
        for c in DEFAULT_DEMO_CASES:
            item = c.copy()
            item["created_at"] = now_iso
            item["updated_at"] = now_iso
            res.append(_format_case_doc(item))
        return res

    query: Dict[str, Any] = {}
    if status_filter and status_filter.lower() != "all":
        norm_status = CaseStatus.normalize(status_filter)
        query["$or"] = [
            {"case_status": {"$regex": f"^{norm_status}$", "$options": "i"}},
            {"case_status": {"$regex": f"^{status_filter}$", "$options": "i"}}
        ]
    if risk_filter and risk_filter.lower() != "all":
        query["risk_level"] = {"$regex": f"^{risk_filter}$", "$options": "i"}
    if animal_id:
        query["animal_id"] = animal_id

    cursor = col.find(query).sort("created_at", -1).skip(skip).limit(limit)
    cases = []
    async for d in cursor:
        cases.append(_format_case_doc(d))
    return cases

async def get_case_by_id(case_id: str) -> VeterinaryCaseResponse:
    col = get_veterinary_cases_collection()
    if col is None:
        for c in DEFAULT_DEMO_CASES:
            if c["case_id"] == case_id:
                now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
                item = c.copy()
                item["created_at"] = now_iso
                item["updated_at"] = now_iso
                return _format_case_doc(item)
        raise HTTPException(status_code=404, detail=f"Case '{case_id}' not found.")

    doc = await col.find_one({"case_id": case_id})
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Veterinary case '{case_id}' was not found."
        )
    return _format_case_doc(doc)

async def create_veterinary_case(
    data: CaseCreateRequest,
    current_user: Optional[Dict[str, Any]] = None
) -> VeterinaryCaseResponse:
    col = get_veterinary_cases_collection()
    if col is None:
        raise HTTPException(status_code=503, detail="Database connection is unavailable.")

    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
    case_id = f"CASE-{datetime.datetime.now().year}-{uuid.uuid4().hex[:8].upper()}"

    # Build AI Assessment detail
    if isinstance(data.ai_assessment, AIAssessmentDetail):
        ai_assess_dict = data.ai_assessment.model_dump()
    elif isinstance(data.ai_assessment, dict):
        ai_assess_dict = data.ai_assessment
    elif isinstance(data.ai_assessment, str):
        ai_assess_dict = {
            "possible_condition": data.ai_assessment,
            "confidence": 85.0,
            "risk_level": data.risk_level,
            "explanation": data.clinical_observations or "Clinical assessment requested.",
            "symptoms_detected": data.symptoms or [],
            "recommended_immediate_actions": ["Physical examination by veterinary officer"],
            "veterinary_review_required": True
        }
    else:
        initial_cond = data.condition or "Undifferentiated Clinical Syndrome"
        ai_assess_dict = {
            "possible_condition": initial_cond,
            "confidence": 75.0,
            "risk_level": data.risk_level,
            "explanation": "Veterinary clinical triage case initiated.",
            "symptoms_detected": data.symptoms or [],
            "recommended_immediate_actions": ["Isolate animal pending veterinarian review"],
            "veterinary_review_required": True
        }

    user_id = current_user.get("sub", "USR-ANONYMOUS") if current_user else "USR-ANONYMOUS"
    user_role = current_user.get("role", "farmer") if current_user else "farmer"
    cond_value = data.condition or ai_assess_dict.get("possible_condition", "Suspected Lumpy Skin Disease")

    case_doc = {
        "case_id": case_id,
        "animal_id": data.animal_id,
        "animal_tag": data.animal_tag or data.animal_id,
        "animal_name": data.animal_name,
        "species": data.species,
        "owner_name": data.owner_name or "Registered Livestock Farmer",
        "location": data.location or "Shed 01",
        "condition": cond_value,
        "risk_level": data.risk_level.upper(),
        "ai_assessment": ai_assess_dict,
        "ai_confidence": float(ai_assess_dict.get("confidence", 85.0)),
        "attending_vet": None,
        "vet_review": None,
        "final_diagnosis": None,
        "treatment_plan": None,
        "treatments": [],
        "follow_up": None,
        "follow_up_date": None,
        "case_status": CaseStatus.PENDING_REVIEW.value,
        "audit_trail": [
            {
                "action": "CASE_CREATED",
                "user_id": user_id,
                "user_role": user_role,
                "details": f"Veterinary case opened for {data.animal_name} ({data.species}). Initial risk: {data.risk_level}.",
                "timestamp": now_iso
            }
        ],
        "created_at": now_iso,
        "updated_at": now_iso
    }

    await col.insert_one(case_doc)
    created = await col.find_one({"case_id": case_id})
    return _format_case_doc(created)

async def review_veterinary_case(
    case_id: str,
    data: CaseReviewRequest,
    current_user: Optional[Dict[str, Any]] = None
) -> VeterinaryCaseResponse:
    col = get_veterinary_cases_collection()
    if col is None:
        raise HTTPException(status_code=503, detail="Database connection is unavailable.")

    existing = await col.find_one({"case_id": case_id})
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Case '{case_id}' was not found for review."
        )

    # Role-based security check
    if current_user:
        user_role = current_user.get("role", "").lower()
        if user_role == "farmer":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access forbidden: Farmers are not authorized to perform clinical reviews or veterinary decisions."
            )

    curr_status = CaseStatus.normalize(existing.get("case_status"))
    if curr_status == CaseStatus.CLOSED.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot review a closed case. Reopening closed cases requires administrative audit."
        )

    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
    vet_name = data.vet_name or (current_user.get("name") if current_user else "Dr. Rajesh Patel")
    vet_id = current_user.get("sub") if current_user else "USR-VET-001"
    vet_license = data.vet_license_no or "VET-REG-88402-GJ"
    decision = data.decision or VetDecision.AI_ASSESSMENT_ACCEPTED.value
    notes = data.clinical_notes or data.review_notes or "Clinical examination completed."
    assessment = data.veterinary_assessment or data.final_diagnosis or "Veterinary assessment documented."

    vet_review_detail = {
        "status": CaseStatus.REVIEWED.value,
        "vet_id": vet_id,
        "vet_name": vet_name,
        "vet_license_no": vet_license,
        "decision": decision,
        "clinical_notes": notes,
        "veterinary_assessment": assessment,
        "reviewed_at": now_iso
    }

    audit_entry = {
        "action": "CASE_REVIEWED",
        "user_id": vet_id,
        "user_role": current_user.get("role", "veterinarian") if current_user else "veterinarian",
        "details": f"Decision: {decision}. Assessment: {assessment}.",
        "timestamp": now_iso
    }

    # Transition PENDING_REVIEW -> REVIEWED (or preserve if already further, or honor explicit requested status)
    if data.case_status:
        new_status = data.case_status
    elif curr_status in [CaseStatus.TREATMENT_ACTIVE.value, CaseStatus.FOLLOW_UP.value]:
        new_status = curr_status
    else:
        new_status = CaseStatus.REVIEWED.value

    update_doc = {
        "$set": {
            "attending_vet": vet_name,
            "vet_review": vet_review_detail,
            "final_diagnosis": assessment,
            "case_status": new_status,
            "follow_up_date": data.follow_up_date or existing.get("follow_up_date"),
            "updated_at": now_iso
        },
        "$push": {
            "audit_trail": audit_entry
        }
    }

    await col.update_one({"case_id": case_id}, update_doc)
    updated = await col.find_one({"case_id": case_id})
    return _format_case_doc(updated)

async def add_case_treatment(
    case_id: str,
    data: CaseTreatmentRequest,
    current_user: Optional[Dict[str, Any]] = None
) -> VeterinaryCaseResponse:
    col = get_veterinary_cases_collection()
    if col is None:
        raise HTTPException(status_code=503, detail="Database connection is unavailable.")

    existing = await col.find_one({"case_id": case_id})
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Case '{case_id}' was not found for treatment."
        )

    # Role-based security check
    if current_user:
        user_role = current_user.get("role", "").lower()
        if user_role == "farmer":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access forbidden: Farmers cannot create prescriptions or veterinary treatment plans."
            )
        if user_role == "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access forbidden: Administrators cannot issue prescription medications without certified veterinary credentials."
            )

    curr_status = CaseStatus.normalize(existing.get("case_status"))
    if curr_status == CaseStatus.PENDING_REVIEW.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Workflow violation: Case must be reviewed by a veterinarian (status REVIEWED) before initiating treatment."
        )
    if curr_status == CaseStatus.CLOSED.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot add treatment to a closed case."
        )

    # License validation
    if data.prescribing_vet_license is not None:
        license_no = data.prescribing_vet_license.strip()
    elif current_user and current_user.get("license"):
        license_no = current_user.get("license").strip()
    else:
        license_no = ""

    if not license_no or len(license_no) < 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A verified, non-empty Veterinary Registration License number is mandatory to approve prescriptions."
        )

    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
    prescribed_by = data.attending_vet_name or (current_user.get("name") if current_user else "Dr. Rajesh Patel")
    diag_assessment = data.diagnosis_assessment or existing.get("final_diagnosis") or "Under Clinical Treatment"

    # Assemble medicines list
    medicines_list: List[Dict[str, Any]] = []
    if data.medicines:
        for m in data.medicines:
            medicines_list.append(m.model_dump())
    elif data.medicine_name:
        medicines_list.append({
            "medicine_name": data.medicine_name,
            "dosage": data.dosage or "Standard dose",
            "frequency": "Once daily",
            "duration": data.duration or "3 days",
            "route": "Intramuscular (IM)",
            "instructions": data.instructions or ""
        })

    # Prepare backward-compatible legacy TreatmentItem
    legacy_treatments = []
    for med in medicines_list:
        treatment_id = f"TRT-{uuid.uuid4().hex[:6].upper()}"
        legacy_treatments.append({
            "treatment_id": treatment_id,
            "medicine_name": med["medicine_name"],
            "dosage": med["dosage"],
            "duration": med["duration"],
            "instructions": med.get("instructions", ""),
            "prescribing_vet_license": license_no,
            "veterinary_approved": True,
            "prescribed_at": now_iso
        })

    treatment_plan_doc = {
        "treatment_id": f"TRT-PLAN-{uuid.uuid4().hex[:6].upper()}",
        "case_id": case_id,
        "veterinary_assessment": diag_assessment,
        "diagnosis_assessment": diag_assessment,
        "medicines": medicines_list,
        "supportive_care": data.supportive_care or "",
        "isolation_required": bool(data.isolation_required if data.isolation_required is not None else True),
        "isolation_instructions": data.isolation_instructions or "Quarantine in isolated pen with vector repellent barrier.",
        "vaccination_advice": data.vaccination_advice or "",
        "prevention_advice": data.prevention_advice or "",
        "instructions": data.instructions or "",
        "farmer_instructions": data.farmer_instructions or "Follow veterinarian's instructions carefully. Do not change prescribed dosage.",
        "prescribed_by": prescribed_by,
        "prescription_license": license_no,
        "treatment_start_date": now_iso[:10],
        "created_at": now_iso,
        "updated_at": now_iso
    }

    audit_entry = {
        "action": "TREATMENT_CREATED",
        "user_id": current_user.get("sub", "USR-VET-001") if current_user else "USR-VET-001",
        "user_role": current_user.get("role", "veterinarian") if current_user else "veterinarian",
        "details": f"Prescribed {len(medicines_list)} medication(s) by {prescribed_by} ({license_no}).",
        "timestamp": now_iso
    }

    update_doc: Dict[str, Any] = {
        "$set": {
            "treatment_plan": treatment_plan_doc,
            "case_status": CaseStatus.TREATMENT_ACTIVE.value,
            "updated_at": now_iso
        },
        "$push": {
            "audit_trail": audit_entry
        }
    }

    # Optional integrated withdrawal
    if data.withdrawal_days is not None:
        if data.withdrawal_days < 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Withdrawal days cannot be negative.")
        start_d = datetime.date.today()
        end_d = start_d + datetime.timedelta(days=data.withdrawal_days)
        w_type = data.withdrawal_type or "milk"
        is_verified = bool(data.withdrawal_verified)
        if is_verified and data.withdrawal_days > 0:
            w_status = "ACTIVE"
            w_notice = f"Mandatory {w_type.upper()} withdrawal active. Discard products for {data.withdrawal_days} more days."
        elif is_verified and data.withdrawal_days == 0:
            w_status = "NO_RESTRICTION"
            w_notice = "No withdrawal restriction active."
        else:
            w_status = "VERIFY_WITH_VETERINARIAN"
            w_notice = "Withdrawal period information is unavailable or unverified. Consult the prescribing veterinarian and applicable food-safety regulations before using milk or meat products."

        update_doc["$set"]["withdrawal_information"] = {
            "withdrawal_type": w_type,
            "withdrawal_days": data.withdrawal_days,
            "withdrawal_start_date": start_d.isoformat(),
            "withdrawal_end_date": end_d.isoformat(),
            "source": data.withdrawal_source or "Statutory Veterinary Prescription Formulary",
            "verified": is_verified,
            "status": w_status,
            "days_remaining": data.withdrawal_days,
            "safety_notice": w_notice
        }

    # Optional initial prevention plan
    if data.isolation_instructions or data.prevention_advice or data.farmer_instructions:
        update_doc["$set"]["prevention_plan"] = {
            "isolation_required": bool(data.isolation_required if data.isolation_required is not None else True),
            "isolation_duration_days": 14,
            "isolation_instructions": data.isolation_instructions or "Separate pen with vector mesh netting.",
            "hygiene_guidance": "Clean and disinfect water troughs and feeding equipment daily.",
            "vector_control": "Apply fly repellent spray and eliminate standing water.",
            "animal_separation": "Zero physical contact with lactating herd cohorts.",
            "monitoring_protocol": "Record body temperature twice daily and log rumination.",
            "farmer_instructions": data.farmer_instructions or "Observe daily feed intake and report any fresh skin eruptions.",
            "updated_at": now_iso
        }

    if legacy_treatments:
        update_doc["$push"]["treatments"] = {"$each": legacy_treatments}

    await col.update_one({"case_id": case_id}, update_doc)
    updated = await col.find_one({"case_id": case_id})
    return _format_case_doc(updated)

async def schedule_case_follow_up(
    case_id: str,
    data: CaseFollowUpRequest,
    current_user: Optional[Dict[str, Any]] = None
) -> VeterinaryCaseResponse:
    col = get_veterinary_cases_collection()
    if col is None:
        raise HTTPException(status_code=503, detail="Database connection is unavailable.")

    existing = await col.find_one({"case_id": case_id})
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Case '{case_id}' was not found."
        )

    if current_user:
        user_role = current_user.get("role", "").lower()
        if user_role == "farmer":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access forbidden: Farmers are not authorized to schedule clinical veterinary follow-ups."
            )

    curr_status = CaseStatus.normalize(existing.get("case_status"))
    if curr_status == CaseStatus.PENDING_REVIEW.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Workflow violation: Case must be reviewed and actively managed before scheduling follow-up."
        )
    if curr_status == CaseStatus.CLOSED.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot schedule follow-up on a closed case."
        )

    # Validate date format (YYYY-MM-DD or standard date format)
    date_str = data.follow_up_date.strip()
    if not re.search(r"\d{4}", date_str):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid follow-up date '{date_str}'. Please provide a valid date string (e.g. YYYY-MM-DD)."
        )

    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
    follow_up_doc = {
        "required": data.required,
        "follow_up_date": date_str,
        "notes": data.notes or "Scheduled re-examination.",
        "completed": False
    }

    audit_entry = {
        "action": "FOLLOW_UP_SCHEDULED",
        "user_id": current_user.get("sub", "USR-VET-001") if current_user else "USR-VET-001",
        "user_role": current_user.get("role", "veterinarian") if current_user else "veterinarian",
        "details": f"Follow-up scheduled for {date_str}. Notes: {data.notes}",
        "timestamp": now_iso
    }

    update_doc = {
        "$set": {
            "follow_up": follow_up_doc,
            "follow_up_date": date_str,
            "case_status": CaseStatus.FOLLOW_UP.value,
            "updated_at": now_iso
        },
        "$push": {
            "audit_trail": audit_entry
        }
    }

    await col.update_one({"case_id": case_id}, update_doc)
    updated = await col.find_one({"case_id": case_id})
    return _format_case_doc(updated)

async def close_veterinary_case(
    case_id: str,
    data: CaseCloseRequest,
    current_user: Optional[Dict[str, Any]] = None
) -> VeterinaryCaseResponse:
    col = get_veterinary_cases_collection()
    if col is None:
        raise HTTPException(status_code=503, detail="Database connection is unavailable.")

    existing = await col.find_one({"case_id": case_id})
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Case '{case_id}' was not found."
        )

    if current_user:
        user_role = current_user.get("role", "").lower()
        if user_role == "farmer":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access forbidden: Farmers are not authorized to close veterinary cases."
            )

    curr_status = CaseStatus.normalize(existing.get("case_status"))
    if curr_status == CaseStatus.CLOSED.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Case is already closed."
        )
    if curr_status == CaseStatus.PENDING_REVIEW.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Workflow violation: Cannot close a case that is pending veterinary review."
        )

    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
    close_notes = data.notes or "Clinical case closed successfully by attending veterinary officer."

    audit_entry = {
        "action": "CASE_CLOSED",
        "user_id": current_user.get("sub", "USR-VET-001") if current_user else "USR-VET-001",
        "user_role": current_user.get("role", "veterinarian") if current_user else "veterinarian",
        "details": close_notes,
        "timestamp": now_iso
    }

    set_fields: Dict[str, Any] = {
        "case_status": CaseStatus.CLOSED.value,
        "updated_at": now_iso
    }
    if existing.get("follow_up"):
        set_fields["follow_up.completed"] = True

    update_doc = {
        "$set": set_fields,
        "$push": {
            "audit_trail": audit_entry
        }
    }

    await col.update_one({"case_id": case_id}, update_doc)
    updated = await col.find_one({"case_id": case_id})
    return _format_case_doc(updated)

async def update_case_prevention(
    case_id: str,
    data: CasePreventionRequest,
    current_user: Optional[Dict[str, Any]] = None
) -> VeterinaryCaseResponse:
    col = get_veterinary_cases_collection()
    if col is None:
        raise HTTPException(status_code=503, detail="Database connection is unavailable.")

    existing = await col.find_one({"case_id": case_id})
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Case '{case_id}' was not found.")

    if current_user:
        user_role = current_user.get("role", "").lower()
        if user_role == "farmer":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access forbidden: Farmers are not authorized to modify veterinary prevention plans."
            )
        if user_role == "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access forbidden: Administrators cannot modify veterinary biosecurity prevention protocols."
            )

    curr_status = CaseStatus.normalize(existing.get("case_status"))
    if curr_status == CaseStatus.CLOSED.value:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot update prevention plan for a closed case.")

    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
    existing_prev = existing.get("prevention_plan") or {}

    prev_doc = {
        "isolation_required": bool(data.isolation_required if data.isolation_required is not None else existing_prev.get("isolation_required", True)),
        "isolation_duration_days": data.isolation_duration_days if data.isolation_duration_days is not None else existing_prev.get("isolation_duration_days", 14),
        "isolation_instructions": data.isolation_instructions or existing_prev.get("isolation_instructions", "Isolate animal in quarantine pen away from healthy herd cohorts."),
        "hygiene_guidance": data.hygiene_guidance or existing_prev.get("hygiene_guidance", "Clean and disinfect water troughs and feeding equipment daily."),
        "vector_control": data.vector_control or existing_prev.get("vector_control", "Apply bio-pesticide fly repellent spray and eliminate standing puddles."),
        "animal_separation": data.animal_separation or existing_prev.get("animal_separation", "Zero physical contact with lactating herd cohorts."),
        "monitoring_protocol": data.monitoring_protocol or existing_prev.get("monitoring_protocol", "Record body temperature twice daily and log rumination activity."),
        "farmer_instructions": data.farmer_instructions or existing_prev.get("farmer_instructions", "Observe daily feed intake and report any fresh skin eruptions."),
        "updated_at": now_iso
    }

    audit_entry = {
        "action": "PREVENTION_PLAN_UPDATED",
        "user_id": current_user.get("sub", "USR-VET-001") if current_user else "USR-VET-001",
        "user_role": current_user.get("role", "veterinarian") if current_user else "veterinarian",
        "details": f"Prevention plan updated. Isolation required: {prev_doc['isolation_required']}.",
        "timestamp": now_iso
    }

    await col.update_one(
        {"case_id": case_id},
        {
            "$set": {"prevention_plan": prev_doc, "updated_at": now_iso},
            "$push": {"audit_trail": audit_entry}
        }
    )
    updated = await col.find_one({"case_id": case_id})
    return _format_case_doc(updated)

async def update_case_withdrawal(
    case_id: str,
    data: CaseWithdrawalRequest,
    current_user: Optional[Dict[str, Any]] = None
) -> VeterinaryCaseResponse:
    col = get_veterinary_cases_collection()
    if col is None:
        raise HTTPException(status_code=503, detail="Database connection is unavailable.")

    existing = await col.find_one({"case_id": case_id})
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Case '{case_id}' was not found.")

    if current_user:
        user_role = current_user.get("role", "").lower()
        if user_role == "farmer":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access forbidden: Farmers cannot modify pharmaceutical withdrawal periods."
            )
        if user_role == "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access forbidden: Administrators cannot modify statutory food-safety withdrawal restrictions."
            )

    if data.withdrawal_days < 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Withdrawal days cannot be negative.")

    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
    try:
        start_d = datetime.date.fromisoformat(data.withdrawal_start_date.split("T")[0]) if data.withdrawal_start_date else datetime.date.today()
    except Exception:
        start_d = datetime.date.today()

    end_d = start_d + datetime.timedelta(days=data.withdrawal_days)
    days_rem = max(0, (end_d - datetime.date.today()).days)

    if data.verified and data.withdrawal_days > 0:
        w_status = "ACTIVE"
        w_notice = f"Mandatory {data.withdrawal_type.upper()} withdrawal active. Discard milk/meat for {days_rem} more days."
        alerts_col = get_alerts_collection()
        if alerts_col is not None:
            alert_doc = {
                "alert_id": f"ALT-{datetime.datetime.now().year}-{uuid.uuid4().hex[:4].upper()}",
                "title": f"Withdrawal Active: {existing.get('animal_tag', existing.get('animal_id'))}",
                "description": f"Mandatory {data.withdrawal_type.upper()} withdrawal period of {data.withdrawal_days} days active until {end_d.isoformat()}.",
                "alert_type": "preventive",
                "severity": "Medium",
                "location": existing.get("location", "Shed 01"),
                "affected_tag": existing.get("animal_tag", existing.get("animal_id")),
                "animal_id": existing.get("animal_id"),
                "action_required": "Do not harvest or sell milk/meat from this animal during withdrawal window.",
                "dispatch_status": "Regulatory Alert Active",
                "status": "Active",
                "created_at": now_iso
            }
            await alerts_col.insert_one(alert_doc)
    elif data.verified and data.withdrawal_days == 0:
        w_status = "NO_RESTRICTION"
        w_notice = "No withdrawal restriction active."
    else:
        w_status = "VERIFY_WITH_VETERINARIAN"
        w_notice = "Withdrawal period information is unavailable or unverified. Consult the prescribing veterinarian and applicable veterinary/food-safety guidance before using milk or meat products."

    withdrawal_doc = {
        "withdrawal_type": data.withdrawal_type,
        "withdrawal_days": data.withdrawal_days,
        "withdrawal_start_date": start_d.isoformat(),
        "withdrawal_end_date": end_d.isoformat(),
        "source": data.source or "Statutory Veterinary Formulation Guide",
        "verified": bool(data.verified),
        "status": w_status,
        "days_remaining": days_rem,
        "safety_notice": w_notice
    }

    audit_entry = {
        "action": "WITHDRAWAL_PERIOD_UPDATED",
        "user_id": current_user.get("sub", "USR-VET-001") if current_user else "USR-VET-001",
        "user_role": current_user.get("role", "veterinarian") if current_user else "veterinarian",
        "details": f"Withdrawal set: {data.withdrawal_days} days for {data.withdrawal_type} (Status: {w_status}).",
        "timestamp": now_iso
    }

    await col.update_one(
        {"case_id": case_id},
        {
            "$set": {"withdrawal_information": withdrawal_doc, "updated_at": now_iso},
            "$push": {"audit_trail": audit_entry}
        }
    )
    updated = await col.find_one({"case_id": case_id})
    return _format_case_doc(updated)

async def add_animal_vaccination(
    animal_id: str,
    data: VaccinationCreateRequest,
    current_user: Optional[Dict[str, Any]] = None
) -> VaccinationRecord:
    col_vac = get_vaccinations_collection()
    if col_vac is None:
        raise HTTPException(status_code=503, detail="Database connection is unavailable.")

    if current_user:
        user_role = current_user.get("role", "").lower()
        if user_role == "farmer":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access forbidden: Farmers are not authorized to log or prescribe official vaccination records."
            )
        if user_role == "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access forbidden: Administrators cannot administer or log clinical vaccines."
            )

    try:
        admin_date = datetime.date.fromisoformat(data.date_administered.split("T")[0])
        due_date = datetime.date.fromisoformat(data.next_due_date.split("T")[0])
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid date format. Expected YYYY-MM-DD.")

    if due_date < admin_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Validation error: Next vaccination due date cannot be earlier than administration date."
        )

    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
    vac_id = f"VAC-{admin_date.year}-{uuid.uuid4().hex[:6].upper()}"

    if due_date < datetime.date.today():
        v_status = "Overdue"
    elif (due_date - datetime.date.today()).days <= 30:
        v_status = "Upcoming"
    else:
        v_status = "Completed"

    administered_by = data.administered_by or (current_user.get("name") if current_user else "Certified Veterinary Officer")

    vac_doc = {
        "vaccination_id": vac_id,
        "animal_id": animal_id,
        "case_id": data.case_id,
        "vaccine_name": data.vaccine_name,
        "disease_target": data.disease_target,
        "date_administered": str(admin_date),
        "next_due_date": str(due_date),
        "batch_number": data.batch_number or "",
        "administered_by": administered_by,
        "notes": data.notes or "",
        "status": v_status,
        "created_at": now_iso
    }

    await col_vac.insert_one(vac_doc)

    # Link to animal record if available
    col_anim = get_animals_collection()
    if col_anim is not None:
        await col_anim.update_one(
            {"$or": [{"animal_id": animal_id}, {"tag": animal_id}]},
            {"$push": {"vaccination_history": vac_doc}}
        )

    # Link to case if provided
    if data.case_id:
        col_case = get_veterinary_cases_collection()
        if col_case is not None:
            audit_entry = {
                "action": "VACCINATION_RECORDED",
                "user_id": current_user.get("sub", "USR-VET-001") if current_user else "USR-VET-001",
                "user_role": current_user.get("role", "veterinarian") if current_user else "veterinarian",
                "details": f"Vaccinated with {data.vaccine_name} for {data.disease_target}. Next due: {str(due_date)}.",
                "timestamp": now_iso
            }
            await col_case.update_one(
                {"case_id": data.case_id},
                {
                    "$set": {"vaccination_record": vac_doc, "updated_at": now_iso},
                    "$push": {"audit_trail": audit_entry}
                }
            )

    vac_doc.pop("_id", None)
    return VaccinationRecord(**vac_doc)

async def get_animal_vaccinations(animal_id: str) -> List[VaccinationRecord]:
    col_vac = get_vaccinations_collection()
    if col_vac is None:
        return []

    cursor = col_vac.find({"animal_id": animal_id}).sort("date_administered", -1)
    results = []
    async for d in cursor:
        d.pop("_id", None)
        results.append(VaccinationRecord(**d))
    return results

async def update_animal_vaccination(
    animal_id: str,
    vaccination_id: str,
    data: VaccinationUpdateRequest,
    current_user: Optional[Dict[str, Any]] = None
) -> VaccinationRecord:
    col_vac = get_vaccinations_collection()
    if col_vac is None:
        raise HTTPException(status_code=503, detail="Database connection is unavailable.")

    if current_user:
        user_role = current_user.get("role", "").lower()
        if user_role in ["farmer", "admin"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access forbidden: Only certified veterinary officers can update vaccination records."
            )

    existing = await col_vac.find_one({"vaccination_id": vaccination_id, "animal_id": animal_id})
    if not existing:
        raise HTTPException(status_code=404, detail=f"Vaccination record '{vaccination_id}' not found for animal '{animal_id}'.")

    update_fields = {k: v for k, v in data.model_dump(exclude_unset=True).items() if v is not None}

    admin_str = update_fields.get("date_administered") or existing.get("date_administered")
    due_str = update_fields.get("next_due_date") or existing.get("next_due_date")

    if admin_str and due_str:
        admin_d = datetime.date.fromisoformat(admin_str.split("T")[0])
        due_d = datetime.date.fromisoformat(due_str.split("T")[0])
        if due_d < admin_d:
            raise HTTPException(status_code=400, detail="Next due date cannot be earlier than administration date.")

    await col_vac.update_one({"vaccination_id": vaccination_id}, {"$set": update_fields})
    updated = await col_vac.find_one({"vaccination_id": vaccination_id})
    updated.pop("_id", None)
    return VaccinationRecord(**updated)

async def get_animal_treatment_history(animal_id: str) -> Dict[str, Any]:
    col = get_veterinary_cases_collection()
    if col is None:
        return {"animal_id": animal_id, "total_cases": 0, "active_treatments": 0, "cases": []}

    cursor = col.find({"$or": [{"animal_id": animal_id}, {"animal_tag": animal_id}]}).sort("created_at", -1)
    cases = []
    active_count = 0
    async for d in cursor:
        case_resp = _format_case_doc(d)
        if case_resp.case_status == CaseStatus.TREATMENT_ACTIVE.value:
            active_count += 1
        cases.append(case_resp)

    return {
        "animal_id": animal_id,
        "total_cases": len(cases),
        "active_treatments": active_count,
        "cases": cases
    }

async def get_veterinary_stats() -> VeterinaryStatsResponse:
    col = get_veterinary_cases_collection()
    if col is None:
        return VeterinaryStatsResponse(
            pending_reviews=1,
            high_critical_cases=2,
            active_treatments=1,
            follow_ups_due=1,
            closed_cases=0,
            total_cases=4,
            vaccinations_due=0,
            withdrawal_restrictions=0
        )

    all_cases = await col.find({}).to_list(1000)
    pending_reviews = 0
    high_critical_cases = 0
    active_treatments = 0
    follow_ups_due = 0
    closed_cases = 0
    withdrawal_restrictions = 0

    for c in all_cases:
        st = CaseStatus.normalize(c.get("case_status"))
        risk = str(c.get("risk_level", "")).upper()

        if st == CaseStatus.PENDING_REVIEW.value:
            pending_reviews += 1
        elif st == CaseStatus.TREATMENT_ACTIVE.value:
            active_treatments += 1
        elif st == CaseStatus.FOLLOW_UP.value:
            follow_ups_due += 1
        elif st == CaseStatus.CLOSED.value:
            closed_cases += 1

        if risk in ["HIGH", "CRITICAL"]:
            high_critical_cases += 1

        w_info = c.get("withdrawal_information") or {}
        if w_info.get("status") == "ACTIVE":
            withdrawal_restrictions += 1

    # Count vaccinations due
    vaccinations_due = 0
    col_vac = get_vaccinations_collection()
    if col_vac is not None:
        try:
            today_str = datetime.date.today().isoformat()
            limit_str = (datetime.date.today() + datetime.timedelta(days=30)).isoformat()
            vaccinations_due = await col_vac.count_documents({
                "$or": [
                    {"status": {"$in": ["Upcoming", "Overdue"]}},
                    {"next_due_date": {"$lte": limit_str}}
                ]
            })
        except Exception:
            vaccinations_due = 0

    return VeterinaryStatsResponse(
        pending_reviews=pending_reviews,
        high_critical_cases=high_critical_cases,
        active_treatments=active_treatments,
        follow_ups_due=follow_ups_due,
        closed_cases=closed_cases,
        total_cases=len(all_cases),
        vaccinations_due=vaccinations_due,
        withdrawal_restrictions=withdrawal_restrictions
    )
