"""
AniCare AI — Multi-Dataset Manifest Generator
Generates reproducible, cryptographic manifests with leakage-resistant train/val/test splits.
"""

import os
import sys
import json
import hashlib
import random
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from PIL import Image

# Ensure backend root on sys.path
backend_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_root))

from app.config import settings

RANDOM_SEED = 42

def sha256_file(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def get_image_info(filepath: Path) -> Tuple[Optional[Tuple[int, int]], Optional[str], Optional[str], Optional[str]]:
    try:
        with Image.open(filepath) as img:
            return img.size, img.format, img.mode, None
    except Exception as e:
        return None, None, None, str(e)

def resolve_path(path_str: str) -> Path:
    p = Path(path_str)
    if p.is_absolute() and p.exists():
        return p
    # Try relative to AniCare-AI root
    anicare_root = backend_root.parent
    if (anicare_root / path_str).exists():
        return anicare_root / path_str
    if (backend_root / path_str).exists():
        return backend_root / path_str
    return p

def generate_disease_manifest(fmd_cattle_dir: Path, archive_dir: Path) -> Dict[str, Any]:
    print("[1/4] Generating Task A (Cattle Disease) Manifest...")
    items = []
    hash_to_items: Dict[str, List[int]] = {}

    # 1. Process FMD_Cattle
    # Folder 0 = Healthy, Folder 1 = FMD
    fmd_cattle_root = fmd_cattle_dir
    if (fmd_cattle_root / "FMD_Cattle").is_dir():
        fmd_cattle_root = fmd_cattle_root / "FMD_Cattle"

    for root, _, files in os.walk(fmd_cattle_root):
        rel_root = Path(root).relative_to(fmd_cattle_root)
        subfolder = str(rel_root).split(os.sep)[0] if str(rel_root) != "." else ""
        
        for fname in sorted(files):
            fpath = Path(root) / fname
            is_backup = fname.endswith(".jpg~")
            ext = fpath.suffix.lower()
            if ext not in [".jpg", ".jpeg", ".png"] and not is_backup:
                continue

            sha = sha256_file(fpath)
            size, fmt, mode, err = get_image_info(fpath)

            class_label = "Healthy / Normal" if subfolder == "0" else ("Foot and Mouth Disease" if subfolder == "1" else "Unknown")
            
            status = "ELIGIBLE"
            reason = None
            if is_backup:
                status = "EXCLUDED"
                reason = "BACKUP_FILE_EXTENSION"
            elif err:
                status = "EXCLUDED"
                reason = f"CORRUPT_IMAGE: {err}"

            item = {
                "id": f"disease_{len(items)+1:05d}",
                "filename": fname,
                "relative_path": str(fpath.relative_to(fmd_cattle_dir)).replace("\\", "/"),
                "absolute_path": str(fpath.resolve()).replace("\\", "/"),
                "dataset_key": "fmd_cattle",
                "dataset_name": "FMD Cattle Lesion Dataset",
                "dataset_source": "ICAR-IVRI / Mendeley Data",
                "task_type": "cattle_disease",
                "class_label": class_label,
                "file_hash": sha,
                "dimensions": list(size) if size else [0, 0],
                "format": fmt or ext.replace(".", "").upper(),
                "mode": mode or "UNKNOWN",
                "file_size_bytes": fpath.stat().st_size,
                "split": "none",
                "exclusion_status": status,
                "exclusion_reason": reason
            }
            items.append(item)
            hash_to_items.setdefault(sha, []).append(len(items) - 1)

    # 2. Process archive (Cows datasets)
    archive_cows_root = archive_dir
    if (archive_dir / "Cows datasets").is_dir():
        archive_cows_root = archive_dir / "Cows datasets"

    for root, _, files in os.walk(archive_cows_root):
        rel_root = Path(root).relative_to(archive_cows_root)
        subfolder = str(rel_root).split(os.sep)[0] if str(rel_root) != "." else ""

        for fname in sorted(files):
            fpath = Path(root) / fname
            ext = fpath.suffix.lower()
            if ext not in [".jpg", ".jpeg", ".png"]:
                continue

            sha = sha256_file(fpath)
            size, fmt, mode, err = get_image_info(fpath)

            if subfolder == "foot-and-mouth":
                class_label = "Foot and Mouth Disease"
            elif subfolder == "lumpy":
                class_label = "Lumpy Skin Disease"
            elif subfolder == "healthy":
                class_label = "Healthy / Normal"
            else:
                class_label = "Unknown"

            status = "ELIGIBLE"
            reason = None
            if "pig" in fname.lower():
                status = "EXCLUDED"
                reason = "EXCLUDED_SPECIES_MISMATCH: Swine/pig lesion image in bovine dataset"
            elif err:
                status = "EXCLUDED"
                reason = f"CORRUPT_IMAGE: {err}"

            item = {
                "id": f"disease_{len(items)+1:05d}",
                "filename": fname,
                "relative_path": str(fpath.relative_to(archive_dir)).replace("\\", "/"),
                "absolute_path": str(fpath.resolve()).replace("\\", "/"),
                "dataset_key": "archive_cows",
                "dataset_name": "Cattle Diseases Kaggle Archive",
                "dataset_source": "Roboflow Universe / Kaggle",
                "task_type": "cattle_disease",
                "class_label": class_label,
                "file_hash": sha,
                "dimensions": list(size) if size else [0, 0],
                "format": fmt or ext.replace(".", "").upper(),
                "mode": mode or "UNKNOWN",
                "file_size_bytes": fpath.stat().st_size,
                "split": "none",
                "exclusion_status": status,
                "exclusion_reason": reason
            }
            items.append(item)
            hash_to_items.setdefault(sha, []).append(len(items) - 1)

    # 3. Detect cross-class duplicates & internal duplicates
    for sha, indices in hash_to_items.items():
        if len(indices) > 1:
            classes = set(items[idx]["class_label"] for idx in indices)
            if len(classes) > 1:
                # Cross-class duplicate! Quarantine all copies
                for idx in indices:
                    items[idx]["exclusion_status"] = "QUARANTINED"
                    items[idx]["exclusion_reason"] = f"CROSS_CLASS_AMBIGUITY: present in classes {sorted(list(classes))}"
            else:
                # Same class duplicate: keep the first as eligible, secondary as DUPLICATE_SECONDARY
                for secondary_idx in indices[1:]:
                    if items[secondary_idx]["exclusion_status"] == "ELIGIBLE":
                        items[secondary_idx]["exclusion_status"] = "INTERNAL_DUPLICATE_RETAINED"
                        items[secondary_idx]["exclusion_reason"] = f"Exact duplicate of {items[indices[0]]['id']}"

    # 4. Stratified Split 70/15/15 for eligible images
    # Group by hash to ensure identical or duplicate images are strictly in the SAME split
    random.seed(RANDOM_SEED)

    by_class: Dict[str, List[str]] = {}
    hash_to_class: Dict[str, str] = {}

    for sha, indices in hash_to_items.items():
        # Only consider if primary item is ELIGIBLE or duplicate
        primary = items[indices[0]]
        if primary["exclusion_status"] in ["ELIGIBLE", "INTERNAL_DUPLICATE_RETAINED"]:
            cls = primary["class_label"]
            by_class.setdefault(cls, []).append(sha)
            hash_to_class[sha] = cls

    hash_to_split: Dict[str, str] = {}
    for cls, hashes in by_class.items():
        random.shuffle(hashes)
        n = len(hashes)
        n_train = int(0.70 * n)
        n_val = int(0.15 * n)
        n_test = n - n_train - n_val

        for i, h in enumerate(hashes):
            if i < n_train:
                hash_to_split[h] = "train"
            elif i < n_train + n_val:
                hash_to_split[h] = "val"
            else:
                hash_to_split[h] = "test"

    for item in items:
        h = item["file_hash"]
        if item["exclusion_status"] in ["ELIGIBLE", "INTERNAL_DUPLICATE_RETAINED"] and h in hash_to_split:
            item["split"] = hash_to_split[h]
        else:
            item["split"] = "none"

    summary = {
        "task": "Task A: Cattle Disease Classification",
        "total_images": len(items),
        "eligible_images": sum(1 for it in items if it["exclusion_status"] in ["ELIGIBLE", "INTERNAL_DUPLICATE_RETAINED"]),
        "quarantined_images": sum(1 for it in items if it["exclusion_status"] == "QUARANTINED"),
        "excluded_images": sum(1 for it in items if it["exclusion_status"] == "EXCLUDED"),
        "classes": {
            cls: sum(1 for it in items if it["class_label"] == cls and it["exclusion_status"] in ["ELIGIBLE", "INTERNAL_DUPLICATE_RETAINED"])
            for cls in ["Healthy / Normal", "Foot and Mouth Disease", "Lumpy Skin Disease"]
        },
        "splits": {
            "train": sum(1 for it in items if it["split"] == "train"),
            "val": sum(1 for it in items if it["split"] == "val"),
            "test": sum(1 for it in items if it["split"] == "test")
        }
    }

    print(f"Task A Manifest ready: {summary['eligible_images']} eligible images. Splits: {summary['splits']}")
    return {"summary": summary, "images": items}

def generate_species_manifest(species_dir: Path) -> Dict[str, Any]:
    print("[2/4] Generating Task B (Animal Species & Breeds) Manifest...")
    items = []
    hash_to_items: Dict[str, List[int]] = {}

    species_mapping = {
        "American Pit Bull Terrier": ("Dog", "American Pit Bull Terrier"),
        "Belgian Shepherd Malinois": ("Dog", "Belgian Shepherd Malinois"),
        "Miniature Schnauzer": ("Dog", "Miniature Schnauzer"),
        "Bengal cats": ("Cat", "Bengal"),
        "Chinchilla (cat)": ("Cat", "Chinchilla"),
        "Persian cats": ("Cat", "Persian"),
        "Charolais cattle": ("Cattle", "Charolais"),
        "Highland cattle": ("Cattle", "Highland"),
        "Holstein Friesian cattle": ("Cattle", "Holstein Friesian"),
        "Anodorhynchus hyacinthinus": ("Bird", "Hyacinth Macaw"),
        "Ara ararauna": ("Bird", "Blue-and-yellow Macaw"),
        "Ara macao": ("Bird", "Scarlet Macaw"),
        "Columba palumbus": ("Bird", "Common Wood Pigeon"),
        "Columbina talpacoti": ("Bird", "Ruddy Ground Dove"),
        "Ocyphaps lophotes": ("Bird", "Crested Pigeon"),
        "Phoeniconaias minor": ("Bird", "Lesser Flamingo"),
        "Phoenicoparrus andinus": ("Bird", "Andean Flamingo"),
        "Phoenicopterus roseus": ("Bird", "Greater Flamingo")
    }

    for root, _, files in os.walk(species_dir):
        rel_root = Path(root).relative_to(species_dir)
        raw_subfolder = str(rel_root).split(os.sep)[0] if str(rel_root) != "." else ""
        subfolder = raw_subfolder.replace("\u200e", "").strip()
        if subfolder not in species_mapping:
            continue

        species, breed = species_mapping[subfolder]

        for fname in sorted(files):
            fpath = Path(root) / fname
            ext = fpath.suffix.lower()
            if ext not in [".jpg", ".jpeg", ".png"]:
                continue

            sha = sha256_file(fpath)
            size, fmt, mode, err = get_image_info(fpath)

            status = "ELIGIBLE"
            reason = None
            if err:
                status = "EXCLUDED"
                reason = f"CORRUPT_IMAGE: {err}"

            item = {
                "id": f"species_{len(items)+1:05d}",
                "filename": fname,
                "relative_path": str(fpath.relative_to(species_dir)).replace("\\", "/"),
                "absolute_path": str(fpath.resolve()).replace("\\", "/"),
                "dataset_key": "class3_species",
                "dataset_name": "Class3 Animal Species & Breeds",
                "dataset_source": "Multi-Species Benchmark",
                "task_type": "species_classification",
                "class_label": species,
                "breed_label": breed,
                "subfolder_class": subfolder,
                "file_hash": sha,
                "dimensions": list(size) if size else [0, 0],
                "format": fmt or ext.replace(".", "").upper(),
                "mode": mode or "UNKNOWN",
                "file_size_bytes": fpath.stat().st_size,
                "split": "none",
                "exclusion_status": status,
                "exclusion_reason": reason
            }
            items.append(item)
            hash_to_items.setdefault(sha, []).append(len(items) - 1)

    # Detect duplicates
    for sha, indices in hash_to_items.items():
        if len(indices) > 1:
            for secondary_idx in indices[1:]:
                items[secondary_idx]["exclusion_status"] = "INTERNAL_DUPLICATE_RETAINED"
                items[secondary_idx]["exclusion_reason"] = f"Duplicate of {items[indices[0]]['id']}"

    # Stratified Split 70/15/15 by species
    random.seed(RANDOM_SEED)
    by_species: Dict[str, List[str]] = {}
    for sha, indices in hash_to_items.items():
        primary = items[indices[0]]
        if primary["exclusion_status"] in ["ELIGIBLE", "INTERNAL_DUPLICATE_RETAINED"]:
            by_species.setdefault(primary["class_label"], []).append(sha)

    hash_to_split: Dict[str, str] = {}
    for sp, hashes in by_species.items():
        random.shuffle(hashes)
        n = len(hashes)
        n_train = int(0.70 * n)
        n_val = int(0.15 * n)
        for i, h in enumerate(hashes):
            if i < n_train:
                hash_to_split[h] = "train"
            elif i < n_train + n_val:
                hash_to_split[h] = "val"
            else:
                hash_to_split[h] = "test"

    for item in items:
        h = item["file_hash"]
        if item["exclusion_status"] in ["ELIGIBLE", "INTERNAL_DUPLICATE_RETAINED"] and h in hash_to_split:
            item["split"] = hash_to_split[h]
        else:
            item["split"] = "none"

    summary = {
        "task": "Task B: Animal Species Classification",
        "total_images": len(items),
        "eligible_images": sum(1 for it in items if it["exclusion_status"] in ["ELIGIBLE", "INTERNAL_DUPLICATE_RETAINED"]),
        "species_counts": {
            sp: sum(1 for it in items if it["class_label"] == sp and it["exclusion_status"] in ["ELIGIBLE", "INTERNAL_DUPLICATE_RETAINED"])
            for sp in ["Cattle", "Dog", "Cat", "Bird"]
        },
        "splits": {
            "train": sum(1 for it in items if it["split"] == "train"),
            "val": sum(1 for it in items if it["split"] == "val"),
            "test": sum(1 for it in items if it["split"] == "test")
        }
    }
    print(f"Task B Manifest ready: {summary['eligible_images']} images. Species: {summary['species_counts']}")
    return {"summary": summary, "images": items}

def generate_muzzle_manifest(muzzle_dir: Path) -> Dict[str, Any]:
    print("[3/4] Generating Task C (Muzzle Biometric Identification) Manifest...")
    items = []
    
    for root, _, files in os.walk(muzzle_dir):
        if not files:
            continue
        rel_root = Path(root).relative_to(muzzle_dir)
        parts = rel_root.parts
        animal_id = "_".join(parts) if parts else "unknown"

        for fname in sorted(files):
            fpath = Path(root) / fname
            ext = fpath.suffix.lower()
            if ext not in [".jpg", ".jpeg", ".png"]:
                continue

            sha = sha256_file(fpath)
            size, fmt, mode, err = get_image_info(fpath)

            status = "ELIGIBLE"
            reason = None
            if err:
                status = "EXCLUDED"
                reason = f"CORRUPT_IMAGE: {err}"

            item = {
                "id": f"muzzle_{len(items)+1:05d}",
                "filename": fname,
                "relative_path": str(fpath.relative_to(muzzle_dir)).replace("\\", "/"),
                "absolute_path": str(fpath.resolve()).replace("\\", "/"),
                "dataset_key": "muzzle_biometrics",
                "dataset_name": "Sahiwal Cattle & Murrah Buffalo Muzzle Dataset",
                "dataset_source": "ICAR-NDRI Karnal / Biometric Registry",
                "task_type": "muzzle_biometrics",
                "animal_id": animal_id,
                "class_label": f"Animal_{animal_id}",
                "clinical_relevance": "NON_CLINICAL_BIOMETRIC_IDENTIFICATION",
                "file_hash": sha,
                "dimensions": list(size) if size else [0, 0],
                "format": fmt or ext.replace(".", "").upper(),
                "mode": mode or "UNKNOWN",
                "file_size_bytes": fpath.stat().st_size,
                "split": "gallery",
                "exclusion_status": status,
                "exclusion_reason": reason
            }
            items.append(item)

    distinct_animals = sorted(list(set(it["animal_id"] for it in items)))
    summary = {
        "task": "Task C: Muzzle Biometric Identification",
        "total_images": len(items),
        "eligible_images": sum(1 for it in items if it["exclusion_status"] == "ELIGIBLE"),
        "distinct_animals": len(distinct_animals),
        "note": "Biometric print recognition. Never use for disease diagnostics."
    }
    print(f"Task C Manifest ready: {summary['eligible_images']} images across {summary['distinct_animals']} animal IDs.")
    return {"summary": summary, "images": items}

def generate_excluded_test_manifest(test_dir: Path) -> Dict[str, Any]:
    print("[4/4] Generating Excluded External Test Manifest...")
    items = []
    
    # Process sample/full unlabelled test folder
    for root, _, files in os.walk(test_dir):
        for fname in sorted(files):
            fpath = Path(root) / fname
            ext = fpath.suffix.lower()
            if ext not in [".jpg", ".jpeg", ".png"]:
                continue

            item = {
                "id": f"test_{len(items)+1:05d}",
                "filename": fname,
                "relative_path": str(fpath.relative_to(test_dir)).replace("\\", "/"),
                "absolute_path": str(fpath.resolve()).replace("\\", "/"),
                "dataset_key": "kaggle_dogs_vs_cats_test",
                "dataset_name": "Kaggle Dogs vs Cats Unlabelled Partition",
                "dataset_source": "Kaggle",
                "task_type": "excluded",
                "class_label": "UNLABELLED",
                "split": "none",
                "exclusion_status": "EXCLUDED",
                "exclusion_reason": "UNLABELLED_PET_DATASET_NON_BOVINE"
            }
            items.append(item)

    summary = {
        "task": "Excluded Unlabelled Test Partition",
        "total_images": len(items),
        "status": "EXCLUDED",
        "reason": "Unlabelled Kaggle domestic animals (Dogs/Cats) without disease ground truth. Cannot be used for evaluation."
    }
    print(f"Excluded Test Manifest ready: {summary['total_images']} images recorded.")
    return {"summary": summary, "images": items}

def main():
    fmd_cattle_dir = resolve_path(settings.DATASET_FMD_CATTLE_DIR)
    archive_dir = resolve_path(settings.DATASET_ARCHIVE_DIR)
    species_dir = resolve_path(settings.DATASET_SPECIES_DIR)
    muzzle_dir = resolve_path(settings.DATASET_MUZZLE_DIR)
    test_dir = resolve_path(settings.DATASET_TEST_DIR)

    manifest_out_dir = resolve_path(settings.DATASETS_MANIFEST_DIR)
    manifest_out_dir.mkdir(parents=True, exist_ok=True)

    print("=======================================================")
    print("AniCare AI — Reproducible Dataset Manifest Generation")
    print(f"Output Directory: {manifest_out_dir}")
    print("=======================================================")

    # 1. Disease manifest
    disease_manifest = generate_disease_manifest(fmd_cattle_dir, archive_dir)
    with open(manifest_out_dir / "manifest_disease_a.json", "w", encoding="utf-8") as f:
        json.dump(disease_manifest, f, indent=2)

    # 2. Species manifest
    species_manifest = generate_species_manifest(species_dir)
    with open(manifest_out_dir / "manifest_species_b.json", "w", encoding="utf-8") as f:
        json.dump(species_manifest, f, indent=2)

    # 3. Muzzle manifest
    muzzle_manifest = generate_muzzle_manifest(muzzle_dir)
    with open(manifest_out_dir / "manifest_muzzle_c.json", "w", encoding="utf-8") as f:
        json.dump(muzzle_manifest, f, indent=2)

    # 4. Excluded manifest
    test_manifest = generate_excluded_test_manifest(test_dir)
    with open(manifest_out_dir / "manifest_test_excluded.json", "w", encoding="utf-8") as f:
        json.dump(test_manifest, f, indent=2)

    # 5. Master summary
    master_summary = {
        "timestamp": "2026-10-09T18:50:00Z",
        "tasks": {
            "task_a_cattle_disease": disease_manifest["summary"],
            "task_b_species_classification": species_manifest["summary"],
            "task_c_muzzle_biometrics": muzzle_manifest["summary"],
            "excluded_external_test": test_manifest["summary"]
        },
        "datasets": [
            {
                "key": "fmd_cattle",
                "name": "FMD Cattle Lesion Dataset",
                "task": "Task A: Cattle Disease Classification",
                "classes": ["Healthy / Normal", "Foot and Mouth Disease"],
                "total_images": 342,
                "provenance": "ICAR-IVRI / Mendeley Data",
                "license": "CC BY 4.0",
                "status": "VERIFIED_ACTIVE"
            },
            {
                "key": "archive_cows",
                "name": "Cows Disease Dataset (archive)",
                "task": "Task A: Cattle Disease Classification",
                "classes": ["Healthy / Normal", "Foot and Mouth Disease", "Lumpy Skin Disease"],
                "total_images": 3244,
                "provenance": "Roboflow Universe / Kaggle",
                "license": "Public Domain / CC0",
                "status": "VERIFIED_ACTIVE"
            },
            {
                "key": "muzzle_biometrics",
                "name": "Sahiwal Cattle & Murrah Buffalo Muzzle Dataset",
                "task": "Task C: Biometric Muzzle Identification",
                "classes": ["77 Individual Animal Muzzle Biometric IDs"],
                "total_images": 1176,
                "provenance": "ICAR-NDRI Karnal / Research Repository",
                "license": "Academic Research Use",
                "status": "VERIFIED_ACTIVE"
            },
            {
                "key": "class3_species",
                "name": "Class3 Animal Species & Breeds Dataset",
                "task": "Task B: Animal Species Classification",
                "classes": ["Cattle", "Dog", "Cat", "Bird"],
                "total_images": 900,
                "provenance": "Multi-Species Computer Vision Benchmark",
                "license": "Open Source / Educational",
                "status": "VERIFIED_ACTIVE"
            },
            {
                "key": "kaggle_dogs_vs_cats_test",
                "name": "Kaggle Dogs vs Cats Unlabelled Partition",
                "task": "Excluded",
                "classes": ["Unlabelled"],
                "total_images": 12500,
                "provenance": "Kaggle Dogs vs Cats Competition",
                "license": "Kaggle Competition Rules",
                "status": "EXCLUDED_UNLABELLED"
            }
        ]
    }
    with open(manifest_out_dir / "datasets_summary.json", "w", encoding="utf-8") as f:
        json.dump(master_summary, f, indent=2)

    print("\n[SUCCESS] All manifests and summary generated successfully!")

if __name__ == "__main__":
    main()
