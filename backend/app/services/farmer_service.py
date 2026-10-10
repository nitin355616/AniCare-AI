import datetime
import uuid
from typing import List, Optional, Dict, Any
from fastapi import HTTPException, status
from app.database import (
    get_animals_collection,
    get_veterinary_cases_collection,
    get_vaccinations_collection,
    get_alerts_collection,
    get_outbreak_events_collection
)
from app.schemas.farmer import (
    FarmerDashboardResponse,
    FarmerAnimalSummary,
    FarmerAnimalDetail,
    FarmerActionStep,
    FarmerTreatmentPlan,
    FarmerMedicine,
    FarmerWithdrawalNotice,
    FarmerVaccinationNotice,
    FarmerFollowUpNotice,
    FarmerOutbreakWarning,
    FarmerReviewRequest,
    FarmerReviewResponse
)
from app.services.animal_service import seed_default_animals_if_empty
from app.services.veterinary_service import seed_default_cases_if_empty

DEMO_FARMER_NAME = "Kishorbhai Patel"
DEMO_FARMER_LOCATION = "Anand District, Gujarat"
DEMO_FARM_KEYWORD = "Amul Co-op Farm #12, Anand, Gujarat"

def _is_owner_match(animal_owner: Optional[str], current_user: Optional[Dict[str, Any]]) -> bool:
    """Checks if an animal belongs to the authenticated user."""
    if not current_user:
        # Default unauthenticated / demo mode: allow demo farm
        if not animal_owner:
            return True
        return ("Patel" in animal_owner or "Amul" in animal_owner or "Anand" in animal_owner)

    user_role = current_user.get("role", "farmer")
    if user_role in ["admin", "veterinarian"]:
        return True

    user_name = (current_user.get("name") or "").strip().lower()
    user_email = (current_user.get("email") or "").strip().lower()
    user_id = (current_user.get("sub") or "").strip().lower()

    if not animal_owner:
        return False

    owner_lower = animal_owner.lower()
    return (
        user_name in owner_lower or
        (user_email and user_email in owner_lower) or
        (user_id and user_id in owner_lower) or
        ("patel" in user_name and "patel" in owner_lower) or
        ("amul" in owner_lower and ("patel" in user_name or "farmer" in user_name or not user_name))
    )

def _build_simplified_status(health_status: str, risk_level: str) -> Dict[str, Any]:
    hs_up = (health_status or "").upper()
    rl_up = (risk_level or "").upper()

    if hs_up in ["CRITICAL", "QUARANTINE"] or rl_up in ["CRITICAL", "HIGH", "HIGH RISK"]:
        return {
            "simplified_status": "URGENT",
            "status_label_en": "Urgent Doctor Attention Needed",
            "status_label_hi": "तत्काल डॉक्टर की जरूरत",
            "explanation_en": "High fever or prominent skin nodules detected. Contact your veterinary doctor immediately.",
            "explanation_hi": "पशु में तेज बुखार या त्वचा पर उभरी हुई गांठें पाई गई हैं। तुरंत पशु चिकित्सक से संपर्क करें।",
            "action_needed": True
        }
    elif hs_up in ["UNDER OBSERVATION", "AT RISK", "RECOVERING"] or rl_up in ["MODERATE", "MODERATE RISK", "MEDIUM"]:
        return {
            "simplified_status": "ATTENTION",
            "status_label_en": "Needs Veterinary Checkup",
            "status_label_hi": "पशु चिकित्सक से जांच कराएं",
            "explanation_en": "AI screening noticed mild unusual signs. A veterinary checkup is recommended.",
            "explanation_hi": "एआई जांच में हल्के असामान्य लक्षण दिखे हैं। पशु चिकित्सक से जांच कराने की सलाह दी जाती है।",
            "action_needed": True
        }
    else:
        return {
            "simplified_status": "HEALTHY",
            "status_label_en": "Healthy & Active",
            "status_label_hi": "स्वस्थ और सक्रिय",
            "explanation_en": "Your animal looks healthy and active. Continue routine care and clean water.",
            "explanation_hi": "आपका पशु बिल्कुल स्वस्थ और सक्रिय दिख रहा है। सामान्य चारा-पानी जारी रखें।",
            "action_needed": False
        }

def _build_action_steps(simplified_status: str) -> List[FarmerActionStep]:
    if simplified_status == "URGENT":
        return [
            FarmerActionStep(
                step_number=1,
                title_en="Isolate Immediately",
                title_hi="तुरंत अलग रखें",
                description_en="Move the animal into a shaded, dry, and insect-proof pen away from other cattle.",
                description_hi="पशु को अन्य मवेशियों से अलग छायादार, सूखे और मच्छर-रोधी बाड़े में रखें।",
                urgency="critical"
            ),
            FarmerActionStep(
                step_number=2,
                title_en="Request Doctor Visit",
                title_hi="डॉक्टर जांच का अनुरोध करें",
                description_en="Use the 'Request Doctor Visit' button below so your assigned veterinary officer is alerted.",
                description_hi="नीचे दिए गए बटन से डॉक्टर जांच का अनुरोध भेजें ताकि आपके डॉक्टर को तुरंत सूचना मिले।",
                urgency="critical"
            ),
            FarmerActionStep(
                step_number=3,
                title_en="Milk Safety Notice",
                title_hi="दूध का उपयोग न करें",
                description_en="Do not consume or sell milk from this cow until the doctor examines and clears it.",
                description_hi="डॉक्टर की अनुमति मिलने तक इस गाय का दूध न पिएं और न ही डेयरी में बेचें।",
                urgency="important"
            ),
            FarmerActionStep(
                step_number=4,
                title_en="Vector Protection",
                title_hi="मक्खी-मच्छर से बचाव",
                description_en="Apply herbal fly repellant or mosquito nets to prevent biting flies from spreading infection.",
                description_hi="काटने वाली मक्खियों से बचाव के लिए नीम का लेप या मच्छरदानी का उपयोग करें।",
                urgency="routine"
            )
        ]
    elif simplified_status == "ATTENTION":
        return [
            FarmerActionStep(
                step_number=1,
                title_en="Close Daily Observation",
                title_hi="दैनिक निगरानी रखें",
                description_en="Watch for fever, changes in milk yield, appetite drop, or new skin spots twice daily.",
                description_hi="दिन में दो बार बुखार, दूध की मात्रा, चारा खाने और त्वचा पर नए दानों पर ध्यान दें।",
                urgency="important"
            ),
            FarmerActionStep(
                step_number=2,
                title_en="Provide Clean Drinking Water",
                title_hi="साफ पानी और सूखा चारा दें",
                description_en="Ensure round-the-clock clean water in separate buckets and keep the stall bedding dry.",
                description_hi="अलग बर्तन में 24 घंटे साफ पीने का पानी दें और बैठने की जगह को सूखा रखें।",
                urgency="routine"
            ),
            FarmerActionStep(
                step_number=3,
                title_en="Consult Veterinary Officer",
                title_hi="पशु चिकित्सक से सलाह लें",
                description_en="If symptoms do not improve within 24 hours, request an in-person veterinary checkup.",
                description_hi="यदि 24 घंटे में सुधार न दिखे, तो पशु चिकित्सक से जांच कराने का अनुरोध करें।",
                urgency="important"
            )
        ]
    else:
        return [
            FarmerActionStep(
                step_number=1,
                title_en="Maintain Shed Hygiene",
                title_hi="बाड़े की नियमित सफाई",
                description_en="Keep the shed floor dry, clean dung regularly, and ensure adequate cross-ventilation.",
                description_hi="बाड़े का फर्श सूखा रखें, गोबर समय पर उठाएं और हवादार वातावरण बनाए रखें।",
                urgency="routine"
            ),
            FarmerActionStep(
                step_number=2,
                title_en="Timely Preventive Vaccination",
                title_hi="समय पर टीकाकरण",
                description_en="Ensure scheduled vaccines for Lumpy Skin, FMD, and HS are up to date before monsoon.",
                description_hi="लंपी, खुरपका-मुंहपका और गलघोंटू के टीके मानसून से पहले अवश्य लगवा लें।",
                urgency="routine"
            ),
            FarmerActionStep(
                step_number=3,
                title_en="Balanced Nutrition",
                title_hi="संतुलित आहार व खनिज",
                description_en="Provide clean drinking water, quality dry and green fodder, and 50g mineral mixture daily.",
                description_hi="साफ पानी, हरा व सूखा चारा और रोजाना 50 ग्राम खनिज मिश्रण दें।",
                urgency="routine"
            )
        ]

async def get_farmer_dashboard(current_user: Optional[Dict[str, Any]] = None) -> FarmerDashboardResponse:
    """Aggregates all animals and health statuses for the requesting farmer."""
    await seed_default_animals_if_empty()
    await seed_default_cases_if_empty()

    animals_col = get_animals_collection()
    cases_col = get_veterinary_cases_collection()
    outbreak_col = get_outbreak_events_collection()

    farmer_name = current_user.get("name", DEMO_FARMER_NAME) if current_user else DEMO_FARMER_NAME
    farmer_location = current_user.get("location", DEMO_FARMER_LOCATION) if current_user else DEMO_FARMER_LOCATION

    # Fetch all animals in database
    all_animals_cursor = animals_col.find({}).sort("created_at", -1) if animals_col is not None else []
    all_animals = await all_animals_cursor.to_list(length=200) if animals_col is not None else []

    # Filter animals owned by this farmer
    user_role = current_user.get("role", "farmer") if current_user else "farmer"
    if user_role in ["admin", "veterinarian"]:
        owned_animals = all_animals
    else:
        owned_animals = [a for a in all_animals if _is_owner_match(a.get("owner"), current_user)]
        # If no animals match the specific new user, return empty list gracefully (privacy preserved)

    # Fetch active cases indexed by animal_id
    cases_cursor = cases_col.find({}).sort("created_at", -1) if cases_col is not None else []
    all_cases = await cases_cursor.to_list(length=200) if cases_col is not None else []
    case_by_animal = {c.get("animal_id"): c for c in all_cases if c.get("animal_id")}

    animal_summaries: List[FarmerAnimalSummary] = []
    healthy_cnt = 0
    attention_cnt = 0
    urgent_cnt = 0

    for a in owned_animals:
        aid = a.get("animal_id")
        case = case_by_animal.get(aid)

        health_status = a.get("health_status", "Healthy")
        risk_level = case.get("risk_level", a.get("risk_level", "Low")) if case else a.get("risk_level", "Low")
        
        status_info = _build_simplified_status(health_status, risk_level)
        simp = status_info["simplified_status"]

        if simp == "URGENT":
            urgent_cnt += 1
        elif simp == "ATTENTION":
            attention_cnt += 1
        else:
            healthy_cnt += 1

        # Determine review status
        rev_status = "NONE"
        has_withdrawal = False
        has_overdue_vac = False

        if case:
            cs = case.get("case_status", "OPEN")
            if cs == "PENDING_REVIEW":
                rev_status = "PENDING"
            elif cs in ["REVIEWED", "EXAMINED"]:
                rev_status = "REVIEWED"
            elif cs in ["IN_TREATMENT", "ACTIVE_TREATMENT"]:
                rev_status = "IN_TREATMENT"

            if case.get("treatment_plan") or case.get("treatments"):
                rev_status = "IN_TREATMENT"

            # Check withdrawal
            wd = case.get("withdrawal")
            if wd and isinstance(wd, dict) and wd.get("is_active"):
                has_withdrawal = True

        animal_summaries.append(
            FarmerAnimalSummary(
                animal_id=aid,
                tag=a.get("tag", "NO-TAG"),
                name=a.get("name", "Animal"),
                species=a.get("species", "Cattle"),
                breed=a.get("breed"),
                age=a.get("age"),
                weight=a.get("weight"),
                photo=a.get("photo"),
                health_status=health_status,
                risk_level=risk_level,
                simplified_status=simp,
                status_label_en=status_info["status_label_en"],
                status_label_hi=status_info["status_label_hi"],
                explanation_en=status_info["explanation_en"],
                explanation_hi=status_info["explanation_hi"],
                action_needed=status_info["action_needed"],
                review_status=rev_status,
                has_active_withdrawal=has_withdrawal,
                has_overdue_vaccine=has_overdue_vac
            )
        )

    # Determine local outbreak warning
    outbreak_warning = FarmerOutbreakWarning(
        has_warning=False,
        severity="NORMAL",
        title_en="Normal Herd Health in Your Area",
        title_hi="आपके क्षेत्र में सामान्य स्थिति",
        message_en="No active epidemic alerts in your village block. Continue routine biosecurity.",
        message_hi="आपके गांव क्षेत्र में किसी बीमारी का प्रकोप नहीं है। सामान्य साफ-सफाई बनाए रखें।",
        action_en="Keep sheds dry and report any unusual symptoms early.",
        action_hi="बाड़े को सूखा रखें और किसी भी नए लक्षण की सूचना तुरंत दें।",
        zone_name=farmer_location
    )

    if outbreak_col is not None:
        try:
            active_outbreak = await outbreak_col.find_one({
                "status": "ACTIVE",
                "risk_tier": {"$in": ["TIER_2_SURVEILLANCE", "TIER_3_RED_ALERT"]}
            })
            if active_outbreak:
                is_red = active_outbreak.get("risk_tier") == "TIER_3_RED_ALERT"
                outbreak_warning = FarmerOutbreakWarning(
                    has_warning=True,
                    severity="HIGH" if is_red else "ELEVATED",
                    title_en="Health Alert for Your District" if is_red else "Increased Health Surveillance in Your Area",
                    title_hi="जिले के लिए स्वास्थ्य चेतावनी" if is_red else "आपके क्षेत्र में पशु स्वास्थ्य निगरानी बढ़ाई गई",
                    message_en="Veterinary officers have stepped up active monitoring in your village cluster. Please inspect your cattle daily for fever or skin nodules.",
                    message_hi="आपके गांव व आसपास के क्षेत्र में पशु डॉक्टरों द्वारा निगरानी बढ़ा दी गई है। कृपया रोजाना अपने पशुओं के शरीर पर गांठ या बुखार की जांच करें।",
                    action_en="Protect cattle from biting flies with repellent, keep sheds clean, and avoid sharing water sources.",
                    action_hi="पशुओं को मक्खी-मच्छरों से बचाएं, बाड़ा साफ रखें और अन्य झुंडों के साथ साझा तालाब में पानी न पिलाएं।",
                    zone_name=farmer_location
                )
        except Exception:
            pass

    return FarmerDashboardResponse(
        farmer_name=farmer_name,
        farmer_location=farmer_location,
        total_animals=len(animal_summaries),
        healthy_count=healthy_cnt,
        attention_count=attention_cnt,
        urgent_count=urgent_cnt,
        outbreak_warning=outbreak_warning,
        animals=animal_summaries
    )

async def get_farmer_animal_detail(animal_id: str, current_user: Optional[Dict[str, Any]] = None) -> FarmerAnimalDetail:
    """Fetches comprehensive, farmer-accessible health dossier with ownership enforcement."""
    await seed_default_animals_if_empty()
    await seed_default_cases_if_empty()

    animals_col = get_animals_collection()
    cases_col = get_veterinary_cases_collection()
    vaccinations_col = get_vaccinations_collection()

    if animals_col is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database service unavailable."
        )

    animal = await animals_col.find_one({"$or": [{"animal_id": animal_id}, {"tag": animal_id}]})
    if not animal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Animal '{animal_id}' was not found in registry."
        )

    # Privacy & Ownership Enforcement
    if current_user and current_user.get("role") == "farmer":
        if not _is_owner_match(animal.get("owner"), current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access forbidden: You do not own this animal. Farmer privacy policy active."
            )

    # Fetch associated veterinary case
    case = None
    if cases_col is not None:
        case = await cases_col.find_one({"animal_id": animal.get("animal_id")})

    health_status = animal.get("health_status", "Healthy")
    risk_level = case.get("risk_level", animal.get("risk_level", "Low")) if case else animal.get("risk_level", "Low")
    status_info = _build_simplified_status(health_status, risk_level)
    simp = status_info["simplified_status"]
    action_steps = _build_action_steps(simp)

    # Review status & Doctor details
    rev_status = "NONE"
    vet_name = None
    treatment_plan: Optional[FarmerTreatmentPlan] = None
    withdrawal_notice: Optional[FarmerWithdrawalNotice] = None
    follow_up_notice: Optional[FarmerFollowUpNotice] = None

    if case:
        cs = case.get("case_status", "OPEN")
        if cs == "PENDING_REVIEW":
            rev_status = "PENDING"
        elif cs in ["REVIEWED", "EXAMINED"]:
            rev_status = "REVIEWED"
        elif cs in ["IN_TREATMENT", "ACTIVE_TREATMENT"]:
            rev_status = "IN_TREATMENT"

        vet_name = case.get("attending_vet")
        vet_review = case.get("vet_review")
        if vet_review and isinstance(vet_review, dict):
            vet_name = vet_name or vet_review.get("vet_name")

        # Treatment Plan
        tp = case.get("treatment_plan")
        treatments = case.get("treatments") or []
        if tp or treatments:
            rev_status = "IN_TREATMENT"
            medicines_list: List[FarmerMedicine] = []
            
            if treatments:
                for tr in treatments:
                    for med in tr.get("medicines", []):
                        medicines_list.append(FarmerMedicine(
                            name=med.get("name", "Prescribed Medication"),
                            dosage=med.get("dosage", "As directed"),
                            frequency=med.get("frequency", "Daily"),
                            duration_days=med.get("duration_days", 5),
                            instructions=med.get("instructions")
                        ))
            elif tp and isinstance(tp, dict):
                for med in tp.get("medicines", []):
                    medicines_list.append(FarmerMedicine(
                        name=med.get("name", "Prescribed Medication"),
                        dosage=med.get("dosage", "As directed"),
                        frequency=med.get("frequency", "Daily"),
                        duration_days=med.get("duration_days", 5),
                        instructions=med.get("instructions")
                    ))

            vet_license = None
            if vet_review and isinstance(vet_review, dict):
                vet_license = vet_review.get("vet_license_no")

            treatment_plan = FarmerTreatmentPlan(
                is_active=True,
                approved_by_vet=vet_name or "Assigned Veterinary Officer",
                vet_license_no=vet_license or "VET-REG-VERIFIED",
                medicines=medicines_list,
                instructions=case.get("treatment_notes") or (tp.get("instructions") if isinstance(tp, dict) else None),
                start_date=case.get("created_at"),
                end_date=case.get("follow_up_date")
            )

        # Withdrawal Notice
        wd = case.get("withdrawal")
        if wd and isinstance(wd, dict) and wd.get("is_active"):
            days_rem = wd.get("days_remaining", 7)
            withdrawal_notice = FarmerWithdrawalNotice(
                is_active=True,
                restriction_type=wd.get("restriction_type", "MILK_AND_MEAT"),
                days_remaining=days_rem,
                end_date=wd.get("end_date"),
                warning_message_en=f"DO NOT sell or consume milk from this cow for the next {days_rem} days.",
                warning_message_hi=f"अगले {days_rem} दिनों तक इस गाय/भैंस का दूध न बेचें और न ही पिएं।"
            )
        else:
            withdrawal_notice = FarmerWithdrawalNotice(
                is_active=False,
                restriction_type="NONE",
                days_remaining=0,
                warning_message_en="No milk or meat withholding restrictions active.",
                warning_message_hi="दूध या मांस पर कोई पाबंदी नहीं है।"
            )

        # Follow-up notice
        fu_date = case.get("follow_up_date")
        if fu_date:
            follow_up_notice = FarmerFollowUpNotice(
                scheduled_date=fu_date,
                is_overdue=False,
                vet_name=vet_name
            )

    # Vaccination notice
    vaccination_notice: Optional[FarmerVaccinationNotice] = None
    if vaccinations_col is not None:
        try:
            vac_doc = await vaccinations_col.find_one({"animal_id": animal.get("animal_id")})
            if vac_doc:
                vaccination_notice = FarmerVaccinationNotice(
                    vaccine_name=vac_doc.get("vaccine_name", "Lumpy Skin Vaccine (Goat Pox)"),
                    target_disease=vac_doc.get("target_disease", "Lumpy Skin Disease"),
                    due_date=vac_doc.get("next_due_date"),
                    is_overdue=vac_doc.get("is_overdue", False),
                    status=vac_doc.get("status", "ACTIVE")
                )
        except Exception:
            pass

    return FarmerAnimalDetail(
        animal_id=animal.get("animal_id"),
        tag=animal.get("tag", "NO-TAG"),
        name=animal.get("name", "Animal"),
        species=animal.get("species", "Cattle"),
        breed=animal.get("breed"),
        age=animal.get("age"),
        weight=animal.get("weight"),
        photo=animal.get("photo"),
        health_status=health_status,
        risk_level=risk_level,
        simplified_status=simp,
        status_label_en=status_info["status_label_en"],
        status_label_hi=status_info["status_label_hi"],
        explanation_en=status_info["explanation_en"],
        explanation_hi=status_info["explanation_hi"],
        action_needed=status_info["action_needed"],
        review_status=rev_status,
        has_active_withdrawal=bool(withdrawal_notice and withdrawal_notice.is_active),
        has_overdue_vaccine=bool(vaccination_notice and vaccination_notice.is_overdue),
        action_steps=action_steps,
        vet_assigned_name=vet_name or "District Veterinary Officer",
        vet_helpline="+91 1800 233 0000",
        treatment_plan=treatment_plan,
        withdrawal_notice=withdrawal_notice,
        vaccination_notice=vaccination_notice,
        follow_up_notice=follow_up_notice,
        recent_symptoms=animal.get("symptoms", []),
        last_checked_date=animal.get("updated_at")
    )

async def request_animal_review(
    animal_id: str,
    request_data: FarmerReviewRequest,
    current_user: Optional[Dict[str, Any]] = None
) -> FarmerReviewResponse:
    """Allows farmer to request an immediate veterinary officer visit for their animal."""
    animals_col = get_animals_collection()
    cases_col = get_veterinary_cases_collection()
    alerts_col = get_alerts_collection()

    if animals_col is None or cases_col is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database service unavailable."
        )

    animal = await animals_col.find_one({"$or": [{"animal_id": animal_id}, {"tag": animal_id}]})
    if not animal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Animal '{animal_id}' was not found."
        )

    # Privacy Check
    if current_user and current_user.get("role") == "farmer":
        if not _is_owner_match(animal.get("owner"), current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access forbidden: You cannot request a visit for an animal you do not own."
            )

    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
    farmer_name = current_user.get("name", animal.get("owner", DEMO_FARMER_NAME)) if current_user else animal.get("owner", DEMO_FARMER_NAME)

    # Check if active case already exists
    existing_case = await cases_col.find_one({"animal_id": animal.get("animal_id")})
    if existing_case:
        case_id = existing_case.get("case_id")
        audit_entry = {
            "action": "FARMER_REVIEW_REQUESTED",
            "user_id": current_user.get("sub", "FARMER-PORTAL") if current_user else "FARMER-PORTAL",
            "user_role": "farmer",
            "details": f"Farmer requested veterinary visit. Notes: {request_data.notes or 'None'}",
            "timestamp": now_iso
        }
        await cases_col.update_one(
            {"case_id": case_id},
            {
                "$set": {"case_status": "PENDING_REVIEW", "updated_at": now_iso},
                "$push": {"audit_trail": audit_entry}
            }
        )
    else:
        case_id = f"CASE-{datetime.datetime.now().year}-{uuid.uuid4().hex[:4].upper()}"
        new_case_doc = {
            "case_id": case_id,
            "animal_id": animal.get("animal_id"),
            "animal_tag": animal.get("tag"),
            "animal_name": animal.get("name"),
            "species": animal.get("species"),
            "owner_name": farmer_name,
            "location": animal.get("location", DEMO_FARMER_LOCATION),
            "risk_level": "HIGH",
            "ai_assessment": {
                "possible_condition": "Suspected Lumpy Skin Disease / Acute Infection",
                "confidence": 85.0,
                "risk_level": "HIGH",
                "explanation": f"Farmer requested emergency doctor review. Reported symptoms: {', '.join(request_data.symptoms or ['Fever/Lethargy'])}",
                "symptoms_detected": request_data.symptoms or ["Farmer Reported Lesions/Fever"],
                "recommended_immediate_actions": ["Isolate animal", "Prompt clinical veterinary review"],
                "veterinary_review_required": True
            },
            "ai_confidence": 85.0,
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
                    "action": "FARMER_REVIEW_REQUESTED",
                    "user_id": current_user.get("sub", "FARMER-PORTAL") if current_user else "FARMER-PORTAL",
                    "user_role": "farmer",
                    "details": f"Farmer requested veterinary examination. Notes: {request_data.notes or 'Prompt visit requested.'}",
                    "timestamp": now_iso
                }
            ],
            "created_at": now_iso,
            "updated_at": now_iso
        }
        await cases_col.insert_one(new_case_doc)

    # Also log an alert for veterinary dashboard
    if alerts_col is not None:
        try:
            alert_id = f"ALT-{uuid.uuid4().hex[:6].upper()}"
            await alerts_col.insert_one({
                "alert_id": alert_id,
                "title": f"Doctor Visit Requested: {animal.get('name')} ({animal.get('tag')})",
                "description": f"Farmer {farmer_name} requested clinical checkup for {animal.get('species')} {animal.get('name')}. Notes: {request_data.notes or 'None'}",
                "severity": "High",
                "alert_type": "disease-risk",
                "location": animal.get("location", DEMO_FARMER_LOCATION),
                "affected_tag": animal.get("tag"),
                "animal_id": animal.get("animal_id"),
                "action_required": "Immediate Clinical Veterinary Checkup",
                "dispatch_status": "Dispatched to Local Dispensary",
                "status": "Active",
                "created_at": now_iso
            })
        except Exception:
            pass

    return FarmerReviewResponse(
        success=True,
        case_id=case_id,
        message_en="Doctor visit requested successfully! Your local veterinary officer has been notified.",
        message_hi="डॉक्टर जांच का अनुरोध सफलतापूर्वक दर्ज हुआ! आपके स्थानीय पशु चिकित्सक को सूचित कर दिया गया है।",
        requested_at=now_iso
    )
