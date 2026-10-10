from typing import Optional
from fastapi import APIRouter, Query, status, HTTPException
from app.schemas.reminder import (
    ReminderCreate,
    ReminderUpdate,
    ReminderResponse,
    ReminderListResponse
)
from app.services.reminder_service import (
    get_reminders,
    create_reminder,
    update_reminder,
    delete_reminder
)

router = APIRouter(prefix="/reminders", tags=["Reminders & Vaccination Schedules"])

@router.get("", response_model=ReminderListResponse, status_code=status.HTTP_200_OK)
async def api_get_reminders(
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status (PENDING, COMPLETED)"),
    reminder_type: Optional[str] = Query(None, description="Filter by type (VACCINATION, VET_APPOINTMENT, HEALTH_CHECK, HYGIENE)"),
    animal_id: Optional[str] = Query(None, description="Filter by animal ID")
):
    """
    Retrieves vaccination schedules, clinical follow-ups, and farm hygiene reminders.
    """
    return await get_reminders(
        status=status_filter,
        reminder_type=reminder_type,
        animal_id=animal_id
    )

@router.post("", response_model=ReminderResponse, status_code=status.HTTP_201_CREATED)
async def api_create_reminder(data: ReminderCreate):
    """
    Creates a new reminder for vaccination, vet appointment, or health follow-up.
    """
    return await create_reminder(data)

@router.put("/{reminder_id}", response_model=ReminderResponse)
async def api_update_reminder(reminder_id: str, data: ReminderUpdate):
    """
    Updates status or details of a reminder.
    """
    res = await update_reminder(reminder_id, data)
    if not res:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Reminder {reminder_id} not found.")
    return res

@router.delete("/{reminder_id}", status_code=status.HTTP_200_OK)
async def api_delete_reminder(reminder_id: str):
    """
    Deletes a reminder.
    """
    success = await delete_reminder(reminder_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Reminder {reminder_id} not found.")
    return {"success": True, "message": f"Reminder {reminder_id} removed."}
