import datetime
import uuid
from typing import List, Optional, Dict, Any
from fastapi import HTTPException, status
from app.database import get_animals_collection
from app.schemas.animal import AnimalCreate, AnimalUpdate, AnimalResponse, AnimalListResponse

DEFAULT_DEMO_ANIMALS = [
  {
    "animal_id": "AN-GJ-2024-0104",
    "tag": "TAG-8821",
    "name": "Ganga",
    "species": "Cattle",
    "breed": "Gir (Indigenous Dairy)",
    "gender": "Female",
    "age": "4.2 years",
    "weight": "440 kg",
    "location": "Shed 04 - Milking Bay A",
    "owner": "Amul Co-op Farm #12, Anand, Gujarat",
    "health_status": "Critical",
    "risk_level": "High Risk",
    "photo": "https://images.unsplash.com/photo-1546445317-29f4545e9d53?auto=format&fit=crop&w=400&q=80",
    "symptoms": ["Excessive ropy salivation", "Vesicular lesions on tongue & gums", "Lameness"],
    "notes": "Exhibiting hypersalivation and lameness. Transferred to Isolation Pen 04."
  },
  {
    "animal_id": "AN-GJ-2024-0412",
    "tag": "TAG-7719",
    "name": "Nandi",
    "species": "Cattle",
    "breed": "Kankrej",
    "gender": "Male",
    "age": "6.0 years",
    "weight": "620 kg",
    "location": "Shed 06 - Breeding Enclosure",
    "owner": "Amul Co-op Farm #12, Anand, Gujarat",
    "health_status": "Critical",
    "risk_level": "High Risk",
    "photo": "https://images.unsplash.com/photo-1500595046743-cd271d694d30?auto=format&fit=crop&w=400&q=80",
    "symptoms": ["Circumscribed 2-5cm skin nodules", "Enlarged lymph nodes", "Persistent pyrexia"],
    "notes": "Widespread cutaneous nodules across neck and perineum. Vector netting installed."
  },
  {
    "animal_id": "AN-GJ-2024-0105",
    "tag": "TAG-8822",
    "name": "Shyamali",
    "species": "Buffalo",
    "breed": "Murrah",
    "gender": "Female",
    "age": "5.5 years",
    "weight": "580 kg",
    "location": "Shed 02 - Lactation Unit",
    "owner": "Amul Co-op Farm #12, Anand, Gujarat",
    "health_status": "Under Observation",
    "risk_level": "Moderate Risk",
    "photo": "https://images.unsplash.com/photo-1527153857715-3908f2bae5e8?auto=format&fit=crop&w=400&q=80",
    "symptoms": ["Right hind quarter swelling", "Conductivity elevation > 6.8 mS/cm"],
    "notes": "CMT test 2+ reaction. Intramammary antibiotic therapy administered."
  },
  {
    "animal_id": "AN-PB-2024-0210",
    "tag": "TAG-9014",
    "name": "Rani",
    "species": "Cattle",
    "breed": "Sahiwal",
    "gender": "Female",
    "age": "3.1 years",
    "weight": "410 kg",
    "location": "Shed 01 - Prime Pasture",
    "owner": "Ludhiana Dairy Collective, Punjab",
    "health_status": "Healthy",
    "risk_level": "Low",
    "photo": "https://images.unsplash.com/photo-1570042225831-d98fa7577f1e?auto=format&fit=crop&w=400&q=80",
    "symptoms": [],
    "notes": "Optimal condition score 3.5/5. Telemetry within normal limits."
  },
  {
    "animal_id": "AN-RJ-2024-0309",
    "tag": "TAG-6119",
    "name": "Badal",
    "species": "Goat",
    "breed": "Jamnapari",
    "gender": "Male",
    "age": "2.0 years",
    "weight": "62 kg",
    "location": "Pen 08 - Small Ruminants",
    "owner": "Bikaner Livestock Centre, Rajasthan",
    "health_status": "Under Observation",
    "risk_level": "Moderate Risk",
    "photo": "https://images.unsplash.com/photo-1524024973431-2ad916746881?auto=format&fit=crop&w=400&q=80",
    "symptoms": ["Mucopurulent nasal catarrh", "Mild stomatitis", "Coughing"],
    "notes": "Isolated in pen 8 following suspected respiratory infection."
  }
]

async def seed_default_animals_if_empty() -> None:
    col = get_animals_collection()
    if col is None:
        return
    count = await col.count_documents({})
    if count == 0:
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
        docs = []
        for a in DEFAULT_DEMO_ANIMALS:
            doc = a.copy()
            doc["created_at"] = now_iso
            doc["updated_at"] = now_iso
            docs.append(doc)
        await col.insert_many(docs)

async def create_animal(data: AnimalCreate) -> AnimalResponse:
    col = get_animals_collection()
    if col is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection is unavailable."
        )

    # Check for duplicate tag
    if data.tag:
        existing = await col.find_one({"tag": data.tag})
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"An animal with ear tag '{data.tag}' is already registered."
            )

    animal_id = f"AN-IND-{uuid.uuid4().hex[:8].upper()}"
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

    doc = {
        "animal_id": animal_id,
        "name": data.name,
        "tag": data.tag,
        "species": data.species,
        "breed": data.breed,
        "gender": data.gender,
        "age": data.age,
        "weight": data.weight,
        "owner": data.owner,
        "photo": data.photo,
        "health_status": data.health_status or "Healthy",
        "risk_level": data.risk_level or "Low",
        "symptoms": data.symptoms or [],
        "location": data.location,
        "notes": data.notes,
        "created_at": now_iso,
        "updated_at": now_iso
    }

    await col.insert_one(doc)
    doc.pop("_id", None)
    return AnimalResponse(**doc)

async def get_animals(
    species: Optional[str] = None,
    health_status: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 100,
    skip: int = 0
) -> AnimalListResponse:
    col = get_animals_collection()
    if col is None:
        # Fallback to in-memory demo items if DB is offline
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
        items = [AnimalResponse(**a, created_at=now_iso, updated_at=now_iso) for a in DEFAULT_DEMO_ANIMALS]
        return AnimalListResponse(total=len(items), items=items)

    query: Dict[str, Any] = {}
    if species and species.lower() != "all":
        query["species"] = {"$regex": f"^{species}$", "$options": "i"}

    if health_status and health_status.lower() != "all":
        if health_status.lower() == "at risk":
            query["health_status"] = {"$in": ["At Risk", "Under Observation"]}
        else:
            query["health_status"] = {"$regex": f"^{health_status}$", "$options": "i"}

    if search:
        search_rgx = {"$regex": search, "$options": "i"}
        query["$or"] = [
            {"name": search_rgx},
            {"tag": search_rgx},
            {"breed": search_rgx},
            {"location": search_rgx},
            {"animal_id": search_rgx}
        ]

    total = await col.count_documents(query)
    cursor = col.find(query).sort("created_at", -1).skip(skip).limit(limit)
    items = []
    async for d in cursor:
        d.pop("_id", None)
        items.append(AnimalResponse(**d))

    return AnimalListResponse(total=total, items=items)

async def get_animal_by_id(animal_id: str) -> AnimalResponse:
    col = get_animals_collection()
    if col is None:
        for a in DEFAULT_DEMO_ANIMALS:
            if a["animal_id"] == animal_id or a["tag"] == animal_id:
                now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
                return AnimalResponse(**a, created_at=now_iso, updated_at=now_iso)
        raise HTTPException(status_code=404, detail=f"Animal '{animal_id}' not found.")

    doc = await col.find_one({"$or": [{"animal_id": animal_id}, {"tag": animal_id}]})
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Animal with ID or Tag '{animal_id}' was not found in the registry."
        )
    doc.pop("_id", None)
    return AnimalResponse(**doc)

async def update_animal(animal_id: str, data: AnimalUpdate) -> AnimalResponse:
    col = get_animals_collection()
    if col is None:
        raise HTTPException(status_code=503, detail="Database connection is unavailable.")

    existing = await col.find_one({"$or": [{"animal_id": animal_id}, {"tag": animal_id}]})
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Animal '{animal_id}' was not found."
        )

    update_fields = {k: v for k, v in data.model_dump(exclude_unset=True).items() if v is not None}
    update_fields["updated_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()

    await col.update_one({"_id": existing["_id"]}, {"$set": update_fields})
    updated = await col.find_one({"_id": existing["_id"]})
    updated.pop("_id", None)
    return AnimalResponse(**updated)

async def delete_animal(animal_id: str) -> Dict[str, Any]:
    col = get_animals_collection()
    if col is None:
        raise HTTPException(status_code=503, detail="Database connection is unavailable.")

    res = await col.delete_one({"$or": [{"animal_id": animal_id}, {"tag": animal_id}]})
    if res.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Animal '{animal_id}' was not found to delete."
        )
    return {"success": True, "message": f"Animal '{animal_id}' removed from registry."}
