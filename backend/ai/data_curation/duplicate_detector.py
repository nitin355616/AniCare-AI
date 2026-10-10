"""
AniCare AI — Duplicate Detection Engine
Implements SHA-256 exact-match detection and 64-bit dHash perceptual
similarity hashing to quarantine duplicate or near-duplicate clinical photographs.
"""

import hashlib
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import numpy as np
from PIL import Image


class DuplicateDetector:
    """
    Guarantees no redundant or near-identical images leak into training datasets
    or compromise validation integrity.
    """

    HAMMING_NEAR_DUPLICATE_THRESHOLD: int = 5

    @classmethod
    def compute_sha256(cls, file_path: str) -> str:
        """Calculates cryptographic SHA-256 digest of file."""
        p = Path(file_path)
        if not p.is_file():
            raise FileNotFoundError(f"File not found: {file_path}")
        h = hashlib.sha256()
        with open(p, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()

    @classmethod
    def compute_dhash(cls, file_path: str, hash_size: int = 8) -> str:
        """
        Computes 64-bit difference hash (dHash) of image.
        Resizes to (hash_size + 1, hash_size) grayscale, compares adjacent columns,
        and converts boolean array to hex string.
        """
        p = Path(file_path)
        if not p.is_file():
            raise FileNotFoundError(f"File not found: {file_path}")

        with Image.open(p) as img:
            # Convert to grayscale and resize to (hash_size + 1, hash_size)
            gray = img.convert("L").resize((hash_size + 1, hash_size), Image.Resampling.BILINEAR)
            arr = np.array(gray, dtype=np.int32)

            # Compare adjacent pixels horizontally: arr[:, 1:] > arr[:, :-1]
            diff = arr[:, 1:] > arr[:, :-1]

            # Convert 64 boolean elements to integer
            val = 0
            for bit in diff.flatten():
                val = (val << 1) | int(bit)

            # Format as 16-character hex string
            return f"{val:016x}"

    @classmethod
    def hamming_distance(cls, hash1: str, hash2: str) -> int:
        """Computes bitwise Hamming distance between two hex perceptual hashes."""
        try:
            val1 = int(hash1, 16)
            val2 = int(hash2, 16)
            xor_val = val1 ^ val2
            return bin(xor_val).count("1")
        except Exception:
            return 64  # Max distance on error

    @classmethod
    def find_duplicates(
        cls,
        candidate_sha: str,
        candidate_dhash: Optional[str],
        known_registry: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Checks a candidate against a registry of known samples.
        Returns:
            is_duplicate: bool
            match_type: "EXACT" | "NEAR_DUPLICATE" | "NONE"
            matched_id: Optional[str]
            distance: int
        """
        for item in known_registry:
            # Exact SHA256 match
            if item.get("sha256") and item["sha256"].lower() == candidate_sha.lower():
                return {
                    "is_duplicate": True,
                    "match_type": "EXACT",
                    "matched_id": item.get("candidate_id") or item.get("id"),
                    "distance": 0,
                    "details": f"Exact cryptographic match with {item.get('candidate_id')}."
                }

            # Near-duplicate perceptual hash match
            if candidate_dhash and item.get("perceptual_hash"):
                dist = cls.hamming_distance(candidate_dhash, item["perceptual_hash"])
                if dist <= cls.HAMMING_NEAR_DUPLICATE_THRESHOLD:
                    return {
                        "is_duplicate": True,
                        "match_type": "NEAR_DUPLICATE",
                        "matched_id": item.get("candidate_id") or item.get("id"),
                        "distance": dist,
                        "details": f"Near-duplicate match (Hamming distance {dist} <= {cls.HAMMING_NEAR_DUPLICATE_THRESHOLD}) with {item.get('candidate_id')}."
                    }

        return {
            "is_duplicate": False,
            "match_type": "NONE",
            "matched_id": None,
            "distance": 64,
            "details": "Unique sample. No duplicate or near-duplicate found."
        }


duplicate_detector = DuplicateDetector()
