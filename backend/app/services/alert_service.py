import datetime
import uuid
from typing import List, Optional, Dict, Any
from fastapi import HTTPException, status
from app.database import get_alerts_collection
from app.schemas.alert import (
    AlertCreate,
    AlertAcknowledgeRequest,
    AlertResponse,
    AlertListResponse
)

DEFAULT_DEMO_ALERTS = [
    {
        "alert_id": "ALT-2026-901",
        "title": "Clustered LSD Outbreak Warning in Sector 04",
        "description": "ANI-NET spatial anomaly detected 7 high-probability Lumpy Skin cases within a 48h temporal window.",
        "alert_type": "critical",
        "severity": "Critical",
        "location": "Anand District, Radius 12km (Surrounding Amul Zone B)",
        "affected_tag": "TAG-7719 + 6 Cohorts",
        "animal_id": "AN-GJ-2024-0412",
        "action_required": "Enact Ring Quarantine & Vector Fumigation",
        "dispatch_status": "Vet Team Dispatched",
        "status": "Active"
    },
    {
        "alert_id": "ALT-2026-902",
        "title": "Acute Hyperthermia Spike in Gir Cattle #8821",
        "description": "Continuous ruminal bolus telemetry logged core temperature rise to 104.8°F accompanied by 42% decrease in rumination.",
        "alert_type": "critical",
        "severity": "Critical",
        "location": "Shed 04 - Milking Bay A",
        "affected_tag": "TAG-8821 (Ganga)",
        "animal_id": "AN-GJ-2024-0104",
        "action_required": "Clinical Examination & Fluid Therapy",
        "dispatch_status": "Pending On-Site Vet Review",
        "status": "Active"
    },
    {
        "alert_id": "ALT-2026-903",
        "title": "Bovine Respiratory Infection Cluster in Pen 08",
        "description": "AI acoustic cough detector logged 4 small ruminants with tachypnea and abnormal coughing frequency.",
        "alert_type": "disease-risk",
        "severity": "High",
        "location": "Pen 08 - Small Ruminants Enclosure",
        "affected_tag": "TAG-6119 + 3 Cohorts",
        "animal_id": "AN-RJ-2024-0309",
        "action_required": "Auscultation & Cohort Isolation",
        "dispatch_status": "Assigned to Dr. Meenakshi",
        "status": "Active"
    },
    {
        "alert_id": "ALT-2026-904",
        "title": "Follow-up Auscultation Due for Calf #2104",
        "description": "Scheduled 48-hour post-treatment evaluation for acute bronchopneumonia recovery monitoring.",
        "alert_type": "follow-up",
        "severity": "Medium",
        "location": "Shed 04 - Recovery Bay",
        "affected_tag": "TAG-2104 (Suraj)",
        "action_required": "Verify Lung Sound Clearance & Temperature",
        "dispatch_status": "Scheduled at 11:30 AM",
        "status": "Active"
    },
    {
        "alert_id": "ALT-2026-905",
        "title": "Brucellosis Booster Due for 42 Heifers",
        "description": "Vaccination window expires in 72 hours under National Animal Disease Control Programme guidelines.",
        "alert_type": "vaccination",
        "severity": "Medium",
        "location": "Shed 01 & Shed 03",
        "affected_tag": "Batch #BR-2026-Q1",
        "action_required": "Confirm Cold-Chain Vaccine Stock & Syringes",
        "dispatch_status": "Stock Reserved in Cold Vault #3",
        "status": "Active"
    },
    {
        "alert_id": "ALT-2026-906",
        "title": "Automated Disinfection Footbath Refill Complete",
        "description": "Sensor indicates sodium carbonate concentration stabilized at 3.98% at vehicle and personnel entryways.",
        "alert_type": "preventive",
        "severity": "Low",
        "location": "Perimeter Gate 1, 2, & Main Parlor",
        "affected_tag": "Bio-Station A-1",
        "action_required": "Routine Weekly Sensor Calibration",
        "dispatch_status": "Completed",
        "status": "Resolved"
    }
]

async def seed_default_alerts_if_empty() -> None:
    col = get_alerts_collection()
    if col is None:
        return
    count = await col.count_documents({})
    if count == 0:
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
        docs = []
        for a in DEFAULT_DEMO_ALERTS:
            doc = a.copy()
            doc["created_at"] = now_iso
            docs.append(doc)
        await col.insert_many(docs)

async def get_alerts(
    alert_type: Optional[str] = None,
    severity: Optional[str] = None,
    status_filter: Optional[str] = None,
    limit: int = 50,
    skip: int = 0
) -> AlertListResponse:
    col = get_alerts_collection()
    if col is None:
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
        items = [AlertResponse(**a, created_at=now_iso) for a in DEFAULT_DEMO_ALERTS]
        return AlertListResponse(total=len(items), unacknowledged=len([i for i in items if i.status == "Active"]), items=items)

    query: Dict[str, Any] = {}
    if alert_type and alert_type.lower() != "all":
        query["alert_type"] = alert_type.lower()
    if severity and severity.lower() != "all":
        query["severity"] = {"$regex": f"^{severity}$", "$options": "i"}
    if status_filter and status_filter.lower() != "all":
        query["status"] = {"$regex": f"^{status_filter}$", "$options": "i"}

    total = await col.count_documents(query)
    unack = await col.count_documents({"status": "Active"})
    cursor = col.find(query).sort("created_at", -1).skip(skip).limit(limit)

    items = []
    async for d in cursor:
        d.pop("_id", None)
        items.append(AlertResponse(**d))

    return AlertListResponse(total=total, unacknowledged=unack, items=items)

async def create_alert(data: AlertCreate) -> AlertResponse:
    col = get_alerts_collection()
    if col is None:
        raise HTTPException(status_code=503, detail="Database connection is unavailable.")

    alert_id = f"ALT-{datetime.datetime.now().year}-{uuid.uuid4().hex[:8].upper()}"
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

    doc = {
        "alert_id": alert_id,
        "title": data.title,
        "description": data.description,
        "alert_type": data.alert_type.value,
        "severity": data.severity.value,
        "location": data.location,
        "affected_tag": data.affected_tag,
        "animal_id": data.animal_id,
        "action_required": data.action_required,
        "dispatch_status": data.dispatch_status or "Alert Logged",
        "status": "Active",
        "created_at": now_iso
    }

    await col.insert_one(doc)
    doc.pop("_id", None)
    return AlertResponse(**doc)

async def acknowledge_alert(alert_id: str, data: AlertAcknowledgeRequest) -> AlertResponse:
    col = get_alerts_collection()
    if col is None:
        raise HTTPException(status_code=503, detail="Database connection is unavailable.")

    existing = await col.find_one({"alert_id": alert_id})
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert '{alert_id}' was not found to acknowledge."
        )

    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
    await col.update_one(
        {"alert_id": alert_id},
        {
            "$set": {
                "status": "Acknowledged",
                "acknowledged_by": data.acknowledged_by,
                "acknowledged_at": now_iso
            }
        }
    )

    updated = await col.find_one({"alert_id": alert_id})
    updated.pop("_id", None)
    return AlertResponse(**updated)
