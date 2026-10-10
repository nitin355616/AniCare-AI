"""
AniCare AI — Milestone 8B Grad-CAM Visualization Generator
Generates and archives Grad-CAM heatmaps for representative test set cases:
- True Positive (TP): ANI-LSD-0098
- False Negative (FN): ANI-LSD-0013
- True Negative (TN): ANI-LSD-0623
- False Positive (FP): ANI-LSD-0381
"""

import json
import shutil
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BACKEND_DIR))

from ai.explainability.gradcam import gradcam_explainer

def run_gradcam_generation():
    manifest_path = BACKEND_DIR / "ai" / "dataset" / "processed" / "manifest.json"
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)
    
    id_to_record = {r["image_id"]: r for r in manifest}

    cases = [
        {"case_type": "TP", "image_id": "ANI-LSD-0098", "target_class_idx": 1, "description": "True Positive: Prominent cutaneous nodular lesions correctly localized"},
        {"case_type": "FN", "image_id": "ANI-LSD-0013", "target_class_idx": 1, "description": "False Negative: Early/subtle lesions diffused across animal flank without focused nodular peak"},
        {"case_type": "TN", "image_id": "ANI-LSD-0623", "target_class_idx": 0, "description": "True Negative: Uniform healthy cutaneous texture without circumscribed activation"},
        {"case_type": "FP", "image_id": "ANI-LSD-0381", "target_class_idx": 1, "description": "False Positive: Prominent natural skin folds and harsh shadow boundaries triggered spurious activation"}
    ]

    output_summary = []
    backend_out = BACKEND_DIR / "uploads" / "explanations"
    backend_out.mkdir(parents=True, exist_ok=True)
    root_out = BACKEND_DIR.parent / "uploads" / "explanations"
    root_out.mkdir(parents=True, exist_ok=True)

    for case in cases:
        img_id = case["image_id"]
        rec = id_to_record[img_id]
        img_path = BACKEND_DIR / rec["file_path"]
        slug = f"{img_id}_{case['case_type'].lower()}"
        print(f"Generating Grad-CAM for {case['case_type']} ({img_id}) at {img_path}...")

        res = gradcam_explainer.generate_heatmap(
            image_path=str(img_path),
            target_class_idx=case["target_class_idx"],
            image_id=slug
        )

        case_info = {
            "case_type": case["case_type"],
            "image_id": img_id,
            "description": case["description"],
            "target_class_idx": case["target_class_idx"],
            "status": res.get("status"),
            "heatmap_filename": res.get("heatmap_filename"),
            "heatmap_url": res.get("heatmap_url"),
            "peak_activation_coords": res.get("peak_activation_coords"),
            "interpretation": res.get("interpretation")
        }
        output_summary.append(case_info)

        # Mirror file to root uploads/explanations if exists
        saved_file = backend_out / f"{slug}_gradcam.jpg"
        if saved_file.is_file():
            shutil.copy2(saved_file, root_out / saved_file.name)

    summary_file = BACKEND_DIR / "ai" / "models" / "evaluation" / "gradcam_case_review.json"
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(output_summary, f, indent=2)

    print(f"Saved {len(output_summary)} Grad-CAM review cases to {summary_file}")
    return output_summary

if __name__ == "__main__":
    run_gradcam_generation()
