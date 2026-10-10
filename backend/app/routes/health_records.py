from fastapi import APIRouter, status
from app.schemas.health_record import HealthRecordCreate, HealthRecordResponse, HealthRecordListResponse
from app.services.health_record_service import create_health_record, get_records_by_animal_id

router = APIRouter(tags=["Health Records"])

@router.post("/health-records", response_model=HealthRecordResponse, status_code=status.HTTP_201_CREATED)
async def api_create_health_record(data: HealthRecordCreate):
    """
    Submits a new physiological telemetry and clinical observations record for an animal.
    """
    return await create_health_record(data)

@router.get("/animals/{animal_id}/health-records", response_model=HealthRecordListResponse)
async def api_get_animal_health_records(animal_id: str):
    """
    Retrieves the clinical chronological health records log for a specific animal.
    """
    return await get_records_by_animal_id(animal_id)
