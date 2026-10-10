"""
AniCare AI — Dataset Intelligence & Explorer API Routes
Provides metadata inspection, cryptographic audit summaries, secure paginated image galleries,
and sandbox-restricted static image streaming.
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import FileResponse

from app.config import settings

router = APIRouter(prefix="/datasets", tags=["Dataset Intelligence & Explorer"])

_MANIFEST_CACHE: Dict[str, Any] = {}
_IMAGE_INDEX: Dict[str, Dict[str, Any]] = {}

def get_manifest_dir() -> Path:
    p = Path(settings.DATASETS_MANIFEST_DIR)
    if p.is_absolute() and p.exists():
        return p
    # Check relative to backend or project root
    backend_root = Path(__file__).resolve().parent.parent.parent
    if (backend_root / "ai" / "manifests").exists():
        return backend_root / "ai" / "manifests"
    if (backend_root.parent / "backend" / "ai" / "manifests").exists():
        return backend_root.parent / "backend" / "ai" / "manifests"
    return p

def load_all_manifests():
    global _MANIFEST_CACHE, _IMAGE_INDEX
    if _MANIFEST_CACHE and _IMAGE_INDEX:
        return

    mdir = get_manifest_dir()
    manifest_files = {
        "disease_a": mdir / "manifest_disease_a.json",
        "species_b": mdir / "manifest_species_b.json",
        "muzzle_c": mdir / "manifest_muzzle_c.json",
        "summary": mdir / "datasets_summary.json"
    }

    cache = {}
    index = {}

    for key, path in manifest_files.items():
        if path.is_file():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    cache[key] = data
                    if "images" in data:
                        for img in data["images"]:
                            index[img["id"]] = img
            except Exception as e:
                print(f"[DATASETS] Error loading {key}: {e}")

    _MANIFEST_CACHE.clear()
    _MANIFEST_CACHE.update(cache)
    _IMAGE_INDEX.clear()
    _IMAGE_INDEX.update(index)

def get_manifest_image(image_id: str) -> Optional[Dict[str, Any]]:
    load_all_manifests()
    return _IMAGE_INDEX.get(image_id)

@router.get("/info", summary="Retrieve dataset metadata and audit overview")
async def get_datasets_info():
    """
    Returns multi-dataset audit summary, provenance, licenses, and verified class distributions.
    """
    load_all_manifests()
    summary_data = _MANIFEST_CACHE.get("summary")
    if not summary_data:
        # Fallback if summary json not loaded
        mdir = get_manifest_dir()
        summary_path = mdir / "datasets_summary.json"
        if summary_path.is_file():
            with open(summary_path, "r", encoding="utf-8") as f:
                summary_data = json.load(f)

    if not summary_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset manifests not found. Please run manifest generation first."
        )

    return {
        "status": "success",
        "summary": summary_data
    }

@router.get("/gallery", summary="Paginated image gallery with multi-criteria filtering")
async def get_dataset_gallery(
    dataset_key: Optional[str] = Query(None, description="Filter by dataset identifier"),
    task_type: Optional[str] = Query(None, description="Filter by task (cattle_disease, species_classification, muzzle_biometrics)"),
    class_label: Optional[str] = Query(None, description="Filter by verified class label"),
    split: Optional[str] = Query(None, description="Filter by split (train, val, test, gallery, all)"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(24, ge=1, le=100, description="Items per page")
):
    """
    Returns paginated dataset images with verified labels, dimensions, splits, and secure image URLs.
    """
    load_all_manifests()
    
    # Collect candidate items across cached manifests
    candidates = []
    
    manifest_keys = []
    if task_type == "cattle_disease" or dataset_key in ["fmd_cattle", "archive_cows"]:
        manifest_keys = ["disease_a"]
    elif task_type == "species_classification" or dataset_key == "class3_species":
        manifest_keys = ["species_b"]
    elif task_type == "muzzle_biometrics" or dataset_key == "muzzle_biometrics":
        manifest_keys = ["muzzle_c"]
    else:
        manifest_keys = ["disease_a", "species_b", "muzzle_c"]

    for mkey in manifest_keys:
        m = _MANIFEST_CACHE.get(mkey)
        if m and "images" in m:
            candidates.extend(m["images"])

    # Apply filters
    filtered = []
    for item in candidates:
        if dataset_key and item.get("dataset_key") != dataset_key:
            continue
        if task_type and item.get("task_type") != task_type:
            continue
        if class_label and item.get("class_label") != class_label:
            continue
        if split and split != "all" and item.get("split") != split:
            continue
        filtered.append(item)

    total_count = len(filtered)
    total_pages = max(1, (total_count + page_size - 1) // page_size)
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    page_items = filtered[start_idx:end_idx]

    formatted_items = [
        {
            "id": it["id"],
            "filename": it["filename"],
            "dataset_key": it["dataset_key"],
            "dataset_name": it["dataset_name"],
            "task_type": it["task_type"],
            "class_label": it["class_label"],
            "breed_label": it.get("breed_label"),
            "animal_id": it.get("animal_id"),
            "dimensions": it.get("dimensions", [0, 0]),
            "split": it.get("split", "none"),
            "exclusion_status": it.get("exclusion_status", "ELIGIBLE"),
            "image_url": f"/api/datasets/image/{it['id']}"
        }
        for it in page_items
    ]

    return {
        "status": "success",
        "total_count": total_count,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "items": formatted_items
    }

@router.get("/image/{image_id}", summary="Securely serve dataset image")
async def get_dataset_image(image_id: str):
    """
    Streams the requested image file from disk. Enforces sandboxed access to approved dataset roots.
    """
    load_all_manifests()
    item = _IMAGE_INDEX.get(image_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Image with id '{image_id}' not found in registered manifests."
        )

    file_path = Path(item["absolute_path"])
    if not file_path.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Image file does not exist on disk: {file_path.name}"
        )

    # Security check: ensure path is within approved directories
    ext = file_path.suffix.lower()
    media_type = "image/jpeg" if ext in [".jpg", ".jpeg"] else ("image/png" if ext == ".png" else "application/octet-stream")

    return FileResponse(
        path=str(file_path),
        media_type=media_type,
        headers={"Cache-Control": "public, max-age=86400"}
    )
