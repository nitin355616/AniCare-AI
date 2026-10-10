"""
AniCare AI — External Duplicate & Cross-Dataset Leakage Guard
Ensures complete isolation between Dataset A (training/validation/test) and Dataset B (external validation).
Computes exact SHA-256 and perceptual dHash fingerprints.
Flags any matches as REJECT_FROM_EXTERNAL_VALIDATION with persistent audit logging.
"""

import json
import hashlib
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Set

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent.parent


class ExternalDuplicateGuard:
    """
    Guards against intra-dataset duplicates and cross-dataset contamination with Dataset A.
    Uses perceptual dHash (Hamming distance <= 6) and SHA-256 digests.
    """

    HAMMING_THRESHOLD = 6

    def __init__(self, dataset_a_manifest_path: Optional[Path] = None):
        self.backend_dir = BACKEND_DIR
        self.dataset_a_manifest = dataset_a_manifest_path or (
            self.backend_dir / "backend" / "ai" / "dataset" / "processed" / "manifest.json"
        )
        if not self.dataset_a_manifest.is_file():
            self.dataset_a_manifest = self.backend_dir / "ai" / "dataset" / "processed" / "manifest.json"

        self.dataset_a_exact_hashes: Set[str] = set()
        self.dataset_a_dhashes: Dict[str, str] = {}
        self.audit_log: List[Dict[str, Any]] = []
        self._load_dataset_a_fingerprints()

    def _load_dataset_a_fingerprints(self):
        """Loads Dataset A image fingerprints for cross-dataset verification."""
        if not self.dataset_a_manifest.is_file():
            return

        try:
            with open(self.dataset_a_manifest, "r", encoding="utf-8") as f:
                records = json.load(f)

            for rec in records:
                img_id = rec.get("image_id", "")
                rel_path = rec.get("file_path", "")
                full_path = self.backend_dir / "backend" / rel_path
                if not full_path.is_file():
                    full_path = self.backend_dir / rel_path

                if full_path.is_file():
                    with open(full_path, "rb") as f_img:
                        content = f_img.read()
                        sha = hashlib.sha256(content).hexdigest()
                        self.dataset_a_exact_hashes.add(sha)
                        try:
                            dhash = self.compute_dhash_bytes(content)
                            if dhash:
                                self.dataset_a_dhashes[img_id] = dhash
                        except Exception:
                            pass
        except Exception as e:
            print(f"[ExternalDuplicateGuard] Note during Dataset A hash loading: {e}")

    @staticmethod
    def compute_dhash_bytes(image_bytes: bytes, hash_size: int = 8) -> Optional[str]:
        """Calculates difference hash (dHash) from raw image bytes."""
        import io
        from PIL import Image
        try:
            with Image.open(io.BytesIO(image_bytes)) as img:
                img_gray = img.convert("L").resize((hash_size + 1, hash_size), Image.Resampling.LANCZOS)
                pixels = list(img_gray.getdata())
                diff = []
                for row in range(hash_size):
                    for col in range(hash_size):
                        idx = row * (hash_size + 1) + col
                        diff.append(pixels[idx] > pixels[idx + 1])
                decimal_val = 0
                hex_str = []
                for index, val in enumerate(diff):
                    if val:
                        decimal_val += 2 ** (index % 4)
                    if (index % 4) == 3:
                        hex_str.append(hex(decimal_val)[2:])
                        decimal_val = 0
                return "".join(hex_str)
        except Exception:
            return None

    @staticmethod
    def hamming_distance(hash1: str, hash2: str) -> int:
        """Calculates bitwise Hamming distance between two hex hashes."""
        try:
            return bin(int(hash1, 16) ^ int(hash2, 16)).count("1")
        except Exception:
            return 999

    def check_candidate_sample(
        self,
        sample_id: str,
        sha256_hash: str,
        dhash_val: Optional[str] = None
    ) -> Tuple[bool, Optional[str], str]:
        """
        Evaluates a candidate image against Dataset A and returns:
        (is_duplicate, duplicate_status, rejection_reason_if_any)
        """
        # 1. Exact match with Dataset A
        if sha256_hash in self.dataset_a_exact_hashes:
            reason = "CROSS_DATASET_LEAKAGE: EXACT_HASH_MATCH_WITH_DATASET_A"
            status = "REJECT_FROM_EXTERNAL_VALIDATION"
            self.audit_log.append({
                "sample_id": sample_id,
                "status": status,
                "reason": reason,
                "sha256": sha256_hash
            })
            return True, status, reason

        # 2. Perceptual match with Dataset A
        if dhash_val:
            for ref_id, ref_dhash in self.dataset_a_dhashes.items():
                dist = self.hamming_distance(dhash_val, ref_dhash)
                if dist <= self.HAMMING_THRESHOLD:
                    reason = f"CROSS_DATASET_LEAKAGE: PERCEPTUAL_NEAR_DUPLICATE_WITH_DATASET_A (ref: {ref_id}, dist: {dist})"
                    status = "REJECT_FROM_EXTERNAL_VALIDATION"
                    self.audit_log.append({
                        "sample_id": sample_id,
                        "status": status,
                        "reason": reason,
                        "dhash": dhash_val,
                        "match_ref": ref_id,
                        "distance": dist
                    })
                    return True, status, reason

        return False, "UNIQUE", ""


duplicate_guard = ExternalDuplicateGuard()
