import datetime
import uuid
import logging
from typing import List, Optional, Dict, Any
from app.database import get_reminders_collection
from app.schemas.reminder import (
    ReminderCreate,
    ReminderUpdate,
    ReminderResponse,
    ReminderListResponse
)

logger = logging.getLogger("anicare.reminder_service")

# In-memory storage for high-availability fallback
_MEMORY_REMINDERS: List[Dict[str, Any]] = [
    {
        "reminder_id": "REM-VACC-001",
        "title": "FMD Booster Vaccination",
        "description": "Foot-and-Mouth Disease bi-annual booster vaccination due for Cattle herd Shed 02.",
        "animal_id": "TAG-8821",
        "animal_tag": "TAG-8821",
        "due_date": "2026-10-15",
        "reminder_type": "VACCINATION",
        "priority": "HIGH",
        "status": "PENDING",
        "created_at": "2026-10-01T08:00:00Z",
        "completed_at": None
    },
    {
        "reminder_id": "REM-CHECK-002",
        "title": "Post-Monsoon De-worming Cycle",
        "description": "Administer broad-spectrum anthelmintic (Albendazole) to all young stock under 18 months.",
        "animal_id": "TAG-4412",
        "animal_tag": "TAG-4412",
        "due_date": "2026-10-18",
        "reminder_type": "HEALTH_CHECK",
        "priority": "MEDIUM",
        "status": "PENDING",
        "created_at": "2026-10-02T09:30:00Z",
        "completed_at": None
    },
    {
        "reminder_id": "REM-HYG-003",
        "title": "Shed Disinfection & Lime Wash",
        "description": "Bi-weekly floor and feeding stall sanitation with sodium carbonate and hydrated lime.",
        "animal_id": None,
        "animal_tag": "All Herd",
        "due_date": "2026-10-20",
        "reminder_type": "HYGIENE",
        "priority": "LOW",
        "status": "PENDING",
        "created_at": "2026-10-03T11:00:00Z",
        "completed_at": None
    },
    {
        "reminder_id": "REM-VET-004",
        "title": "Dr. Arvind Verma Clinical Follow-Up",
        "description": "Review recovery of Cow #8821 following treatment for acute respiratory signs.",
        "animal_id": "TAG-8821",
        "animal_tag": "TAG-8821",
        "due_date": "2026-10-12",
        "reminder_type": "VET_APPOINTMENT",
        "priority": "HIGH",
        "status": "PENDING",
        "created_at": "2026-10-05T14:15:00Z",
        "completed_at": None
    }
]

async def seed_default_reminders_if_empty() -> None:
    col = get_reminders_collection()
    if col is not None:
        try:
            count = await col.count_documents({})
            if count == 0:
                await col.insert_many([dict(r) for r in _MEMORY_REMINDERS])
                logger.info("Default reminders seeded into MongoDB.")
        except Exception as e:
            logger.warning(f"Note during reminder seeding: {e}")

async def get_reminders(
    status: Optional[str] = None,
    reminder_type: Optional[str] = None,
    animal_id: Optional[str] = None
) -> ReminderListResponse:
    col = get_reminders_collection()
    if col is not None:
        try:
            query = {}
            if status:
                query["status"] = status
            if reminder_type:
                query["reminder_type"] = reminder_type
            if animal_id:
                query["animal_id"] = animal_id

            cursor = col.find(query, {"_id": 0}).sort("due_date", 1)
            docs = await cursor.to_list(length=200)
            if docs:
                return ReminderListResponse(total=len(docs), items=[ReminderResponse(**d) for d in docs])
        except Exception as e:
            logger.warning(f"Error querying reminders from Mongo, using memory fallback: {e}")

    # Fallback in-memory
    filtered = list(_MEMORY_REMINDERS)
    if status:
        filtered = [r for r in filtered if r.get("status") == status]
    if reminder_type:
        filtered = [r for r in filtered if r.get("reminder_type") == reminder_type]
    if animal_id:
        filtered = [r for r in filtered if r.get("animal_id") == animal_id]

    return ReminderListResponse(total=len(filtered), items=[ReminderResponse(**r) for r in filtered])

async def create_reminder(data: ReminderCreate) -> ReminderResponse:
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
    reminder_id = f"REM-{uuid.uuid4().hex[:8].upper()}"

    doc = {
        "reminder_id": reminder_id,
        "title": data.title,
        "description": data.description or "",
        "animal_id": data.animal_id,
        "animal_tag": data.animal_tag or data.animal_id,
        "due_date": data.due_date,
        "reminder_type": data.reminder_type,
        "priority": data.priority,
        "status": "PENDING",
        "created_at": now_iso,
        "completed_at": None
    }

    col = get_reminders_collection()
    if col is not None:
        try:
            await col.insert_one(dict(doc))
        except Exception as e:
            logger.warning(f"Failed to insert reminder into MongoDB: {e}")

    _MEMORY_REMINDERS.insert(0, doc)
    return ReminderResponse(**doc)

async def update_reminder(reminder_id: str, data: ReminderUpdate) -> Optional[ReminderResponse]:
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
    updates = {k: v for k, v in data.model_dump().items() if v is not None}
    if updates.get("status") == "COMPLETED" and "completed_at" not in updates:
        updates["completed_at"] = now_iso

    col = get_reminders_collection()
    if col is not None:
        try:
            await col.update_one({"reminder_id": reminder_id}, {"$set": updates})
            doc = await col.find_one({"reminder_id": reminder_id}, {"_id": 0})
            if doc:
                return ReminderResponse(**doc)
        except Exception as e:
            logger.warning(f"Failed to update reminder in MongoDB: {e}")

    # Fallback in-memory
    for r in _MEMORY_REMINDERS:
        if r["reminder_id"] == reminder_id:
            r.update(updates)
            return ReminderResponse(**r)
    return None

async def delete_reminder(reminder_id: str) -> bool:
    global _MEMORY_REMINDERS
    col = get_reminders_collection()
    if col is not None:
        try:
            res = await col.delete_one({"reminder_id": reminder_id})
            if res.deleted_count > 0:
                _MEMORY_REMINDERS = [r for r in _MEMORY_REMINDERS if r["reminder_id"] != reminder_id]
                return True
        except Exception as e:
            logger.warning(f"Failed to delete reminder from MongoDB: {e}")

    initial_len = len(_MEMORY_REMINDERS)
    _MEMORY_REMINDERS = [r for r in _MEMORY_REMINDERS if r["reminder_id"] != reminder_id]
    return len(_MEMORY_REMINDERS) < initial_len
