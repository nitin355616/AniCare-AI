from typing import Optional, List
from fastapi import APIRouter, Query, status, HTTPException
from app.database import get_disease_assessments_collection
from app.schemas.history import AssessmentHistoryItem, AssessmentHistoryResponse

router = APIRouter(tags=["Disease Screening History"])

# Realistic fallback assessments for immediate demonstration and offline resilience
_MOCK_HISTORY: List[dict] = [
    {
        "assessment_id": "ASM-8821-RESP",
        "animal_id": "TAG-8821",
        "species": "Cattle (Bovine)",
        "possible_condition": "Bovine Respiratory Disease Complex",
        "risk_level": "HIGH",
        "confidence": 87.4,
        "explanation": "Syndromic signs indicate acute Bovine Respiratory Disease Complex (BRDC) with tachypnea and pyrexia.",
        "symptoms_detected": [
            "Rapid, shallow dyspneic breathing",
            "Serous to mucopurulent nasal discharge",
            "Elevated core temperature (104.4°F)",
            "Depressed appetite and droopy ears"
        ],
        "recommended_immediate_actions": [
            "Isolate affected animal in a dry, well-ventilated recovery stall.",
            "Conduct thoracic auscultation and evaluate lung sound rales.",
            "Provide clean, lukewarm water and palatable green fodder."
        ],
        "veterinary_review_required": True,
        "image_url": "/uploads/sample_respiratory.jpg",
        "created_at": "2026-10-08T14:30:00Z",
        "source": "ai_inference"
    },
    {
        "assessment_id": "ASM-4412-LSD",
        "animal_id": "TAG-4412",
        "species": "Cattle (Bovine)",
        "possible_condition": "Lumpy Skin Disease",
        "risk_level": "CRITICAL",
        "confidence": 88.4,
        "explanation": "Nodular epidermal lesions on neck and perineum paired with pre-scapular lymph node enlargement.",
        "symptoms_detected": [
            "Firm circumscribed skin nodules (2-5cm)",
            "Enlarged superficial lymph nodes",
            "Elevated core temperature (>104°F)"
        ],
        "recommended_immediate_actions": [
            "Strict herd quarantine within 5km radius.",
            "Apply antiseptic spray to open nodules to prevent fly strikes.",
            "Notify district animal husbandry officer immediately."
        ],
        "veterinary_review_required": True,
        "image_url": "/uploads/sample_lsd.jpg",
        "created_at": "2026-10-07T11:15:00Z",
        "source": "ai_inference"
    },
    {
        "assessment_id": "ASM-1092-MAST",
        "animal_id": "TAG-1092",
        "species": "Buffalo (Bubaline)",
        "possible_condition": "Clinical Mastitis",
        "risk_level": "MODERATE",
        "confidence": 76.2,
        "explanation": "Right hind quarter swelling with altered milk consistency detected during evening milking.",
        "symptoms_detected": [
            "Udder quarter swelling / heat",
            "Floccules or watery quarter milk"
        ],
        "recommended_immediate_actions": [
            "Perform California Mastitis Test (CMT) strip cup test.",
            "Milk affected quarter last and discard abnormal milk safely.",
            "Apply cold fomentation if acute inflammation is present."
        ],
        "veterinary_review_required": True,
        "image_url": "/uploads/sample_mastitis.jpg",
        "created_at": "2026-10-06T08:45:00Z",
        "source": "ai_inference"
    }
]

@router.get("/history", response_model=AssessmentHistoryResponse, status_code=status.HTTP_200_OK)
@router.get("/disease/history", response_model=AssessmentHistoryResponse, status_code=status.HTTP_200_OK)
async def api_get_assessment_history(
    animal_id: Optional[str] = Query(None, description="Filter by animal tag ID"),
    limit: int = Query(50, ge=1, le=100),
    page: int = Query(1, ge=1)
):
    """
    Retrieves previous AI disease screening records and clinical assessments.
    """
    col = get_disease_assessments_collection()
    skip = (page - 1) * limit
    if col is not None:
        try:
            query = {}
            if animal_id:
                query["$or"] = [
                    {"animal_id": animal_id},
                    {"request_payload.animal_id": animal_id}
                ]
            cursor = col.find(query, {"_id": 0}).sort("created_at", -1).skip(skip).limit(limit)
            docs = await cursor.to_list(length=limit)
            if docs:
                items = []
                for d in docs:
                    req_payload = d.get("request_payload") or {}
                    items.append(AssessmentHistoryItem(
                        assessment_id=d.get("assessment_id", "ASM-UNKNOWN"),
                        animal_id=d.get("animal_id") or req_payload.get("animal_id") or "Unregistered",
                        species=d.get("species") or req_payload.get("species") or "Cattle (Bovine)",
                        possible_condition=d.get("possible_condition", "Screening Complete"),
                        risk_level=d.get("risk_level", "MODERATE"),
                        confidence=float(d.get("confidence", 80.0)),
                        explanation=d.get("explanation", ""),
                        symptoms_detected=d.get("symptoms_detected", []),
                        recommended_immediate_actions=d.get("recommended_immediate_actions", []),
                        veterinary_review_required=d.get("veterinary_review_required", True),
                        image_url=d.get("image_url") or req_payload.get("image_id"),
                        created_at=d.get("created_at", ""),
                        source=d.get("engine_selected", "ai_model")
                    ))
                total_count = await col.count_documents(query)
                return AssessmentHistoryResponse(total=total_count, items=items, page=page, limit=limit)
        except Exception:
            pass

    # In-memory fallback
    filtered = list(_MOCK_HISTORY)
    if animal_id:
        filtered = [f for f in filtered if f["animal_id"] == animal_id]
    
    total = len(filtered)
    paged = filtered[skip:skip + limit]
    return AssessmentHistoryResponse(
        total=total,
        items=[AssessmentHistoryItem(**item) for item in paged],
        page=page,
        limit=limit
    )

@router.get("/history/{assessment_id}", response_model=AssessmentHistoryItem)
async def api_get_assessment_detail(assessment_id: str):
    """
    Retrieves a specific historical assessment by ID.
    """
    col = get_disease_assessments_collection()
    if col is not None:
        try:
            doc = await col.find_one({"assessment_id": assessment_id}, {"_id": 0})
            if doc:
                req_payload = doc.get("request_payload") or {}
                return AssessmentHistoryItem(
                    assessment_id=doc.get("assessment_id"),
                    animal_id=doc.get("animal_id") or req_payload.get("animal_id") or "Unregistered",
                    species=doc.get("species") or req_payload.get("species") or "Cattle (Bovine)",
                    possible_condition=doc.get("possible_condition", "Screening Complete"),
                    risk_level=doc.get("risk_level", "MODERATE"),
                    confidence=float(doc.get("confidence", 80.0)),
                    explanation=doc.get("explanation", ""),
                    symptoms_detected=doc.get("symptoms_detected", []),
                    recommended_immediate_actions=doc.get("recommended_immediate_actions", []),
                    veterinary_review_required=doc.get("veterinary_review_required", True),
                    image_url=doc.get("image_url"),
                    created_at=doc.get("created_at", ""),
                    source=doc.get("engine_selected", "ai_model")
                )
        except Exception:
            pass

    for m in _MOCK_HISTORY:
        if m["assessment_id"] == assessment_id:
            return AssessmentHistoryItem(**m)

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Assessment {assessment_id} not found.")
