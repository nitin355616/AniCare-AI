from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Query, status, Depends
from app.schemas.animal import AnimalCreate, AnimalUpdate, AnimalResponse, AnimalListResponse
from app.schemas.veterinary import (
    VaccinationRecord,
    VaccinationCreateRequest,
    VaccinationUpdateRequest
)
from app.services.animal_service import (
    create_animal,
    get_animals,
    get_animal_by_id,
    update_animal,
    delete_animal
)
from app.services.veterinary_service import (
    add_animal_vaccination,
    get_animal_vaccinations,
    update_animal_vaccination,
    get_animal_treatment_history
)
from app.routes.veterinary import get_optional_user

router = APIRouter(prefix="/animals", tags=["Animals Registry"])

@router.post("", response_model=AnimalResponse, status_code=status.HTTP_201_CREATED)
async def api_create_animal(data: AnimalCreate):
    """
    Registers a new livestock animal in the central surveillance registry.
    """
    return await create_animal(data)

@router.get("", response_model=AnimalListResponse)
async def api_get_animals(
    species: Optional[str] = Query(None, description="Filter by species (Cattle, Buffalo, Goat, Sheep)"),
    health_status: Optional[str] = Query(None, description="Filter by status (Healthy, At Risk, Quarantine, Critical, Recovering)"),
    search: Optional[str] = Query(None, description="Search by animal name, tag, breed, or location"),
    limit: int = Query(100, ge=1, le=500),
    skip: int = Query(0, ge=0)
):
    """
    Retrieves livestock animal registry with multi-criteria filtering and pagination.
    """
    return await get_animals(species=species, health_status=health_status, search=search, limit=limit, skip=skip)

@router.get("/{animal_id}", response_model=AnimalResponse)
async def api_get_animal(animal_id: str):
    """
    Retrieves full profile for a specific animal by its animal_id or RFID tag.
    """
    return await get_animal_by_id(animal_id)

@router.put("/{animal_id}", response_model=AnimalResponse)
async def api_update_animal(animal_id: str, data: AnimalUpdate):
    """
    Updates clinical status, location, or biometrics for an animal.
    """
    return await update_animal(animal_id, data)

@router.delete("/{animal_id}")
async def api_delete_animal(animal_id: str):
    """
    Removes an animal from the registry.
    """
    return await delete_animal(animal_id)

# ==================== Milestone 9B: Vaccination & Treatment History ====================

@router.get("/{animal_id}/vaccinations", response_model=List[VaccinationRecord])
async def api_get_animal_vaccinations(animal_id: str):
    """
    Retrieves complete official vaccination records and upcoming boosters for an animal.
    Accessible to farmers, veterinarians, and administrators.
    """
    return await get_animal_vaccinations(animal_id)

@router.post("/{animal_id}/vaccinations", response_model=VaccinationRecord, status_code=status.HTTP_201_CREATED)
async def api_add_animal_vaccination(
    animal_id: str,
    data: VaccinationCreateRequest,
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """
    Records an authorized veterinary vaccine administration with batch number and booster due date.
    Restricted to certified Veterinary Medical Officers.
    """
    return await add_animal_vaccination(animal_id, data, current_user=current_user)

@router.put("/{animal_id}/vaccinations/{vaccination_id}", response_model=VaccinationRecord)
async def api_update_animal_vaccination(
    animal_id: str,
    vaccination_id: str,
    data: VaccinationUpdateRequest,
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """
    Updates booster date, notes, or batch number for an existing vaccination entry.
    Restricted to certified Veterinary Medical Officers.
    """
    return await update_animal_vaccination(animal_id, vaccination_id, data, current_user=current_user)

@router.get("/{animal_id}/treatment-history")
async def api_get_animal_treatment_history(animal_id: str):
    """
    Retrieves chronological medical cases, prescribed medications, and clinical decisions for an animal.
    """
    return await get_animal_treatment_history(animal_id)
