import datetime
from fastapi import APIRouter, UploadFile, File, HTTPException, status
from app.schemas.detection import (
    ImageUploadResponse,
    DetectionAnalyzeRequest,
    DetectionAnalyzeResponse
)
from app.utils.file_storage import save_uploaded_image
from app.services.detection_service import analyze_disease

router = APIRouter(prefix="/detection", tags=["AI Disease Detection"])
disease_router = APIRouter(prefix="/disease", tags=["AI Disease Detection"])

@router.post(
    "/upload",
    response_model=ImageUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload animal photo for AI screening"
)
@disease_router.post(
    "/upload",
    response_model=ImageUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload animal photo for AI screening (disease alias)"
)
async def upload_animal_photo(file: UploadFile = File(...)):
    """
    Accepts JPG, PNG, WEBP animal images up to 10MB.
    Validates magic bytes, assigns a safe unique UUID, and stores in non-executable storage.
    """
    result = await save_uploaded_image(file)
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
    return ImageUploadResponse(
        image_id=result["image_id"],
        filename=result["filename"],
        original_filename=result["original_filename"],
        content_type=result["content_type"],
        file_size_bytes=result["file_size_bytes"],
        url=result["url"],
        created_at=now_iso
    )

@router.post(
    "/analyze",
    response_model=DetectionAnalyzeResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze multi-parameter animal telemetry and symptoms"
)
@disease_router.post(
    "/analyze",
    response_model=DetectionAnalyzeResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze multi-parameter animal telemetry and symptoms (disease alias)"
)
async def analyze_animal_condition(payload: DetectionAnalyzeRequest):
    """
    Executes rule-based Demo Inference Engine simulation adhering to the
    future ML model contract. Returns structured condition, confidence, risk score,
    explanation, recommended actions, and differential diagnoses.
    """
    return await analyze_disease(payload)


from pathlib import Path
from typing import Optional, Dict, Any
from pydantic import BaseModel

class RealPredictRequest(BaseModel):
    image_id: Optional[str] = None


def resolve_any_image(image_id: str) -> Optional[str]:
    """Resolves an image identifier from user uploads or verified dataset manifests."""
    from app.services.detection_service import resolve_uploaded_image_path
    p = resolve_uploaded_image_path(image_id)
    if p and Path(p).is_file():
        return p
    try:
        from app.routes.datasets import get_manifest_image
        item = get_manifest_image(image_id)
        if item and Path(item.get("absolute_path", "")).is_file():
            return item["absolute_path"]
    except Exception:
        pass
    return None


@router.post(
    "/predict-real",
    status_code=status.HTTP_200_OK,
    summary="Execute genuine neural network disease prediction on uploaded or dataset image"
)
@router.get(
    "/predict-real",
    status_code=status.HTTP_200_OK,
    summary="Execute genuine neural network disease prediction (GET)"
)
async def predict_real_disease(
    image_id: Optional[str] = None,
    payload: Optional[RealPredictRequest] = None
):
    """
    Executes genuine PyTorch MobileNetV2 inference trained on verified FMD and LSD cattle datasets.
    Returns real softmax confidence scores, risk level, differential probabilities, and triage actions.
    Supports uploaded photos as well as verified dataset sample IDs.
    """
    target_id = (payload.image_id if payload and payload.image_id else None) or image_id
    if not target_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing image_id. Provide image_id via query param or JSON payload."
        )

    image_path = resolve_any_image(target_id)
    if not image_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Image '{target_id}' not found in uploads or registered dataset manifests."
        )

    from app.services.multi_model_service import multi_model_service
    try:
        res = multi_model_service.predict_disease(image_path)
        res["image_id"] = target_id
        return res
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid or unreadable image file: {str(e)}"
        )
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Model service unavailable: {str(e)}"
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Inference execution failure. Please try again."
        )


@router.post(
    "/validate-species",
    status_code=status.HTTP_200_OK,
    summary="Validate animal species before clinical diagnosis"
)
@router.get(
    "/validate-species",
    status_code=status.HTTP_200_OK,
    summary="Validate animal species before clinical diagnosis (GET)"
)
async def validate_animal_species(
    image_id: Optional[str] = None,
    payload: Optional[RealPredictRequest] = None
):
    """
    Executes Task B Species Guard model to verify if image contains Cattle, Dog, Cat, or Bird.
    """
    target_id = (payload.image_id if payload and payload.image_id else None) or image_id
    if not target_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing image_id. Provide image_id via query param or JSON payload."
        )

    image_path = resolve_any_image(target_id)
    if not image_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Image '{target_id}' not found in uploads or registered dataset manifests."
        )

    from app.services.multi_model_service import multi_model_service
    try:
        res = multi_model_service.predict_species(image_path)
        res["image_id"] = target_id
        return res
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid or unreadable image file: {str(e)}"
        )
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Species model service unavailable: {str(e)}"
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Species validation execution failure. Please try again."
        )


@router.get(
    "/muzzle-registry",
    status_code=status.HTTP_200_OK,
    summary="Retrieve Task C biometric muzzle identification profiles"
)
async def get_muzzle_profiles():
    """
    Returns registered individual bovine animals indexed by muzzle prints.
    """
    from app.services.multi_model_service import get_muzzle_registry
    reg = get_muzzle_registry()
    if not reg:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Muzzle registry not loaded."
        )
    return reg

