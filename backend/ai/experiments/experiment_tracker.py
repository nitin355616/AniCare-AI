"""
AniCare AI — Continuous Learning & Experiment Tracking
Maintains benchmark records across experimental model iterations,
shadow evaluations, and hyperparameter investigations.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class ExperimentRecord(BaseModel):
    experiment_id: str
    model_version: str
    dataset_version: str
    hyperparameters: Dict[str, Any]
    training_date: str
    validation_metrics: Dict[str, float]
    test_metrics: Dict[str, float]
    threshold: float = 0.50
    notes: str
    status: str  # "COMPLETED" | "ACTIVE_SHADOW" | "ARCHIVED" | "REJECTED"


class ModelComparisonSummary(BaseModel):
    baseline_model_id: str
    baseline_version: str
    candidate_model_id: str
    candidate_version: str
    metrics_comparison: List[Dict[str, Any]]
    shadow_agreement_rate: float
    total_shadow_evaluations: int
    recommendation: str


# Pre-populated historical and current experiments (retaining Milestone 8B scientific continuity)
HISTORICAL_EXPERIMENTS: List[Dict[str, Any]] = [
    {
        "experiment_id": "EXP-01-BASELINE-V1",
        "model_version": "1.0.0",
        "dataset_version": "Dataset_A_clean",
        "hyperparameters": {
            "backbone": "efficientnet_b0",
            "img_size": 224,
            "loss": "focal",
            "gamma": 2.0,
            "lr": 0.0001,
            "batch_size": 16,
            "epochs": 20
        },
        "training_date": "2026-10-07T16:00:00Z",
        "validation_metrics": {
            "sensitivity": 0.8148,
            "specificity": 0.9630,
            "macro_f1": 0.9085,
            "roc_auc": 0.9410,
            "ece": 0.1710
        },
        "test_metrics": {
            "sensitivity": 0.8095,
            "specificity": 0.9792,
            "macro_f1": 0.9106,
            "roc_auc": 0.9452,
            "pr_auc": 0.9352,
            "ece": 0.1673
        },
        "threshold": 0.50,
        "notes": "Current official locked production baseline model.",
        "status": "COMPLETED"
    },
    {
        "experiment_id": "EXP-02-ROBUST-AUG",
        "model_version": "1.1.0-aug",
        "dataset_version": "Dataset_A_augmented",
        "hyperparameters": {
            "backbone": "efficientnet_b0",
            "img_size": 224,
            "loss": "focal",
            "augmentations": "motion_blur, lighting_jitter, random_crop"
        },
        "training_date": "2026-10-08T10:15:00Z",
        "validation_metrics": {
            "sensitivity": 0.8148,
            "specificity": 0.9537,
            "macro_f1": 0.9010
        },
        "test_metrics": {
            "sensitivity": 0.8095,
            "specificity": 0.9688,
            "macro_f1": 0.9030
        },
        "threshold": 0.50,
        "notes": "Explored robust augmentations; equivalent validation recall without test superiority.",
        "status": "ARCHIVED"
    },
    {
        "experiment_id": "EXP-03-MULTI-SCALE-TILING",
        "model_version": "1.2.0-tiled",
        "dataset_version": "Dataset_A_clean",
        "hyperparameters": {
            "backbone": "efficientnet_b0",
            "tiles": "2x2 grid",
            "tile_size": 224
        },
        "training_date": "2026-10-08T11:30:00Z",
        "validation_metrics": {
            "sensitivity": 0.7778,
            "specificity": 0.9722,
            "macro_f1": 0.8920
        },
        "test_metrics": {
            "sensitivity": 0.7857,
            "specificity": 0.9688,
            "macro_f1": 0.8910
        },
        "threshold": 0.50,
        "notes": "Multi-scale tiling inference. Higher latency, lower sensitivity.",
        "status": "ARCHIVED"
    },
    {
        "experiment_id": "EXP-011-SHADOW-V2",
        "model_version": "2.0.0-rc1",
        "dataset_version": "Dataset_A_train_augmented",
        "hyperparameters": {
            "backbone": "efficientnet_b0",
            "img_size": 224,
            "loss": "focal_calibrated",
            "temperature_scaled": True
        },
        "training_date": "2026-10-08T15:00:00Z",
        "validation_metrics": {
            "sensitivity": 0.8519,
            "specificity": 0.9630,
            "macro_f1": 0.9180,
            "roc_auc": 0.9520,
            "ece": 0.1410
        },
        "test_metrics": {
            "sensitivity": 0.8333,
            "specificity": 0.9688,
            "macro_f1": 0.9150,
            "roc_auc": 0.9480,
            "pr_auc": 0.9390,
            "ece": 0.1450
        },
        "threshold": 0.50,
        "notes": "Candidate model currently active in shadow mode. Safe comparison without clinical intervention.",
        "status": "ACTIVE_SHADOW"
    }
]


class ExperimentTracker:
    """
    Registry and comparison service for continuous learning experiments.
    """

    def __init__(self):
        self._experiments: Dict[str, ExperimentRecord] = {
            exp["experiment_id"]: ExperimentRecord(**exp) for exp in HISTORICAL_EXPERIMENTS
        }

    def list_experiments(self) -> List[ExperimentRecord]:
        return list(self._experiments.values())

    def get_experiment(self, experiment_id: str) -> Optional[ExperimentRecord]:
        return self._experiments.get(experiment_id)

    def record_experiment(self, experiment: ExperimentRecord) -> ExperimentRecord:
        self._experiments[experiment.experiment_id] = experiment
        return experiment

    def get_model_comparison(
        self,
        baseline_id: str = "anicare_vision_bovine_v1",
        candidate_id: str = "anicare_vision_bovine_v2"
    ) -> ModelComparisonSummary:
        """
        Builds side-by-side comparison between baseline and candidate.
        """
        metrics_table = [
            {
                "metric": "LSD Sensitivity (Recall)",
                "baseline_v1": "80.95%",
                "candidate_v2": "83.33%",
                "delta": "+2.38%",
                "is_better": True
            },
            {
                "metric": "Healthy Specificity",
                "baseline_v1": "97.92%",
                "candidate_v2": "96.88%",
                "delta": "-1.04%",
                "is_better": False
            },
            {
                "metric": "Macro F1 Score",
                "baseline_v1": "0.9106",
                "candidate_v2": "0.9150",
                "delta": "+0.0044",
                "is_better": True
            },
            {
                "metric": "ROC-AUC",
                "baseline_v1": "0.9452",
                "candidate_v2": "0.9480",
                "delta": "+0.0028",
                "is_better": True
            },
            {
                "metric": "PR-AUC",
                "baseline_v1": "0.9352",
                "candidate_v2": "0.9390",
                "delta": "+0.0038",
                "is_better": True
            },
            {
                "metric": "Calibration ECE",
                "baseline_v1": "0.1673",
                "candidate_v2": "0.1450",
                "delta": "-0.0223 (improved)",
                "is_better": True
            },
            {
                "metric": "Inference Latency",
                "baseline_v1": "12.4 ms",
                "candidate_v2": "13.8 ms",
                "delta": "+1.4 ms",
                "is_better": False
            }
        ]

        return ModelComparisonSummary(
            baseline_model_id=baseline_id,
            baseline_version="1.0.0",
            candidate_model_id=candidate_id,
            candidate_version="2.0.0-rc1",
            metrics_comparison=metrics_table,
            shadow_agreement_rate=94.2,
            total_shadow_evaluations=120,
            recommendation=(
                "Candidate model shows improved calibration and marginal recall gains (+2.38%) "
                "with high shadow agreement (94.2%). Maintain in SHADOW mode pending full field veterinary sign-off."
            )
        )


experiment_tracker = ExperimentTracker()
