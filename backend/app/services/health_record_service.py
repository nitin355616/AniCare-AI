import datetime
import uuid
from typing import List, Optional
from fastapi import HTTPException, status
from app.database import get_health_records_collection
from app.schemas.health_record import HealthRecordCreate, HealthRecordResponse, HealthRecordListResponse

DEFAULT_DEMO_RECORDS = [
    {
        "id": "REC-001",
        "animal_id": "AN-GJ-2024-0104",
        "symptoms": ["Excessive ropy salivation", "Vesicular lesions on tongue and gums"],
        "temperature": "104.8 °F",
        "appetite": "Anorexic (Refusing fodder)",
        "activity": "Recumbent / Reluctant to stand",
        "breathing": "Rapid / Dyspneic",
        "observations": "Oral mucosal lesions stage 2. Fluid swab collected for RT-PCR.",
        "previous_conditions": ["Routine health screening clear Aug 2026"],
        "vaccination_status": "FMD Quadrivalent booster valid",
        "recorded_by": "Dr. Rajesh Patel",
        "timestamp": "2026-10-06T09:15:00Z"
    },
    {
        "id": "REC-002",
        "animal_id": "AN-GJ-2024-0104",
        "symptoms": ["Core temperature elevation"],
        "temperature": "103.5 °F",
        "appetite": "Reduced by 30%",
        "activity": "Lethargic",
        "breathing": "Slightly elevated",
        "observations": "Early hyperthermia trend detected by ruminal sensor.",
        "previous_conditions": [],
        "vaccination_status": "FMD Quadrivalent booster valid",
        "recorded_by": "IoT Bolus Node #GJ-04",
        "timestamp": "2026-10-05T18:00:00Z"
    }
]

async def seed_default_health_records_if_empty() -> None:
    col = get_health_records_collection()
    if col is None:
        return
    count = await col.count_documents({})
    if count == 0:
        await col.insert_many([r.copy() for r in DEFAULT_DEMO_RECORDS])

async def create_health_record(data: HealthRecordCreate) -> HealthRecordResponse:
    col = get_health_records_collection()
    if col is None:
        raise HTTPException(status_code=503, detail="Database connection is unavailable.")

    record_id = f"REC-{uuid.uuid4().hex[:8].upper()}"
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

    doc = {
        "id": record_id,
        "animal_id": data.animal_id,
        "symptoms": data.symptoms,
        "temperature": data.temperature,
        "appetite": data.appetite,
        "activity": data.activity,
        "breathing": data.breathing,
        "observations": data.observations,
        "previous_conditions": data.previous_conditions,
        "vaccination_status": data.vaccination_status,
        "recorded_by": data.recorded_by or "Attendant",
        "timestamp": now_iso
    }

    await col.insert_one(doc)
    doc.pop("_id", None)
    return HealthRecordResponse(**doc)

async def get_records_by_animal_id(animal_id: str) -> HealthRecordListResponse:
    col = get_health_records_collection()
    if col is None:
        matched = [HealthRecordResponse(**r) for r in DEFAULT_DEMO_RECORDS if r["animal_id"] == animal_id]
        return HealthRecordListResponse(animal_id=animal_id, total=len(matched), records=matched)

    cursor = col.find({"animal_id": animal_id}).sort("timestamp", -1)
    records = []
    async for d in cursor:
        d.pop("_id", None)
        records.append(HealthRecordResponse(**d))

    return HealthRecordListResponse(animal_id=animal_id, total=len(records), records=records)
