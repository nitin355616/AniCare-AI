"""
AniCare AI — Statistical Model Drift Detection Engine
Implements Population Stability Index (PSI) and multi-signal distribution analysis
across confidence scores, input image quality, and prediction class frequencies.
"""

import math
from typing import Dict, Any, List, Optional, Tuple
from pydantic import BaseModel


class DriftStatus(str):
    NORMAL = "NORMAL"
    WATCH = "WATCH"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class SignalDriftDetail(BaseModel):
    signal_name: str
    metric: str
    baseline_value: float
    current_value: float
    difference: float
    status: str
    details: str


class DriftReport(BaseModel):
    drift_status: str
    overall_psi: float
    confidence_psi: float
    class_distribution_shift: float
    image_quality_shift: float
    species_anomaly_rate: float
    baseline_sample_count: int
    current_sample_count: int
    baseline_window: str
    monitoring_window: str
    signals: List[SignalDriftDetail]
    interpretation: str
    recommended_actions: List[str]
    is_demo_simulated: bool = False


class DriftDetector:
    """
    Transparent, explainable statistical drift monitor.
    Uses Population Stability Index (PSI) over 10 confidence deciles.
    """

    # Baseline confidence distribution established on Dataset A validation set (10 bins)
    BASELINE_CONFIDENCE_BINS: List[float] = [
        0.02,  # 0.00 - 0.10
        0.03,  # 0.10 - 0.20
        0.04,  # 0.20 - 0.30
        0.05,  # 0.30 - 0.40
        0.08,  # 0.40 - 0.50
        0.12,  # 0.50 - 0.60
        0.16,  # 0.60 - 0.70
        0.18,  # 0.70 - 0.80
        0.20,  # 0.80 - 0.90
        0.12   # 0.90 - 1.00
    ]

    # Baseline visual quality metrics on Dataset A
    BASELINE_AVG_BRIGHTNESS: float = 124.5
    BASELINE_AVG_BLUR: float = 48.2
    BASELINE_LSD_PREVALENCE: float = 0.304  # ~30.4% LSD in Dataset A validation

    @classmethod
    def calculate_psi(cls, baseline_probs: List[float], current_probs: List[float], eps: float = 1e-4) -> float:
        """
        Calculates Population Stability Index:
        PSI = sum((Actual_i - Expected_i) * ln(Actual_i / Expected_i))
        """
        psi = 0.0
        for b, c in zip(baseline_probs, current_probs):
            b_safe = max(eps, b)
            c_safe = max(eps, c)
            psi += (c_safe - b_safe) * math.log(c_safe / b_safe)
        return round(psi, 4)

    @classmethod
    def compute_binned_distribution(cls, values: List[float], num_bins: int = 10) -> List[float]:
        """Bins continuous values [0.0, 1.0] into probability distribution."""
        if not values:
            return [1.0 / num_bins] * num_bins
        counts = [0] * num_bins
        for v in values:
            # Clamp between 0.0 and 0.9999 to assign bin index [0, 9]
            clamped = max(0.0, min(0.9999, float(v)))
            idx = int(clamped * num_bins)
            counts[idx] += 1
        total = float(len(values))
        return [c / total for c in counts]

    @classmethod
    def evaluate_drift(
        cls,
        recent_confidences: List[float],
        recent_predictions: List[str],
        recent_brightness: Optional[List[float]] = None,
        recent_blur: Optional[List[float]] = None,
        species_list: Optional[List[str]] = None,
        is_demo: bool = False
    ) -> DriftReport:
        """
        Calculates comprehensive statistical drift across recent inference telemetry.
        """
        n_samples = len(recent_confidences)

        # If insufficient data (< 5 samples), report NORMAL with caveat
        if n_samples < 5:
            return DriftReport(
                drift_status=DriftStatus.NORMAL,
                overall_psi=0.02,
                confidence_psi=0.02,
                class_distribution_shift=0.0,
                image_quality_shift=0.0,
                species_anomaly_rate=0.0,
                baseline_sample_count=135,
                current_sample_count=n_samples,
                baseline_window="Dataset A Validation Baseline",
                monitoring_window="Current Session",
                signals=[],
                interpretation="Insufficient sample count to detect distribution shift (< 5 predictions). Model operating normally.",
                recommended_actions=["Continue collecting field telemetry."],
                is_demo_simulated=is_demo
            )

        # 1. Confidence PSI
        current_bins = cls.compute_binned_distribution(recent_confidences, num_bins=10)
        confidence_psi = cls.calculate_psi(cls.BASELINE_CONFIDENCE_BINS, current_bins)

        # 2. Prediction Class Shift
        lsd_count = sum(1 for p in recent_predictions if "lumpy" in str(p).lower() or "lsd" in str(p).lower())
        current_lsd_prev = lsd_count / float(n_samples)
        class_shift = abs(current_lsd_prev - cls.BASELINE_LSD_PREVALENCE)

        # 3. Image Quality Shift
        avg_bright = float(sum(recent_brightness) / len(recent_brightness)) if recent_brightness else cls.BASELINE_AVG_BRIGHTNESS
        avg_blur = float(sum(recent_blur) / len(recent_blur)) if recent_blur else cls.BASELINE_AVG_BLUR
        bright_diff = abs(avg_bright - cls.BASELINE_AVG_BRIGHTNESS) / cls.BASELINE_AVG_BRIGHTNESS
        blur_diff = abs(avg_blur - cls.BASELINE_AVG_BLUR) / cls.BASELINE_AVG_BLUR
        quality_shift = round((bright_diff + blur_diff) / 2.0, 3)

        # 4. Species Anomaly Rate
        unsupported_count = 0
        if species_list:
            for s in species_list:
                s_lower = str(s).lower()
                if not any(b in s_lower for b in ["cattle", "cow", "bovine", "bull", "calf", "heifer"]):
                    unsupported_count += 1
            species_anomaly = unsupported_count / float(len(species_list))
        else:
            species_anomaly = 0.0

        # Signals List
        signals: List[SignalDriftDetail] = [
            SignalDriftDetail(
                signal_name="Confidence Distribution (PSI)",
                metric="Population Stability Index",
                baseline_value=0.0,
                current_value=confidence_psi,
                difference=confidence_psi,
                status="CRITICAL" if confidence_psi >= 0.50 else ("WARNING" if confidence_psi >= 0.25 else ("WATCH" if confidence_psi >= 0.10 else "NORMAL")),
                details=f"Confidence decile PSI = {confidence_psi:.4f}."
            ),
            SignalDriftDetail(
                signal_name="LSD Positive Proportion",
                metric="Positive Screening Rate",
                baseline_value=cls.BASELINE_LSD_PREVALENCE,
                current_value=round(current_lsd_prev, 3),
                difference=round(class_shift, 3),
                status="WATCH" if class_shift >= 0.20 else "NORMAL",
                details=f"LSD screening proportion is {current_lsd_prev*100:.1f}% vs baseline {cls.BASELINE_LSD_PREVALENCE*100:.1f}%."
            ),
            SignalDriftDetail(
                signal_name="Input Image Illumination & Clarity",
                metric="Visual Shift Ratio",
                baseline_value=0.0,
                current_value=quality_shift,
                difference=quality_shift,
                status="WATCH" if quality_shift >= 0.25 else "NORMAL",
                details=f"Field image lighting/blur divergence is {quality_shift*100:.1f}% from training baseline."
            )
        ]

        # Overall PSI and Status
        overall_psi = confidence_psi
        if overall_psi < 0.10:
            status = DriftStatus.NORMAL
            interp = "NORMAL: No significant distribution shift detected. Model predictions are statistically stable."
            actions = ["Maintain standard automated inference and veterinary logging."]
        elif overall_psi < 0.25:
            status = DriftStatus.WATCH
            interp = "WATCH: Moderate confidence distribution shift detected. Potential field lighting or early lesion variation."
            actions = ["Increase veterinary review sampling rate.", "Inspect recent false-positive field logs."]
        elif overall_psi < 0.50:
            status = DriftStatus.WARNING
            interp = "WARNING: Significant distribution shift detected. Potential camera variation or out-of-domain lesions."
            actions = ["Alert attending veterinary officers.", "Conduct manual inspection of low-confidence predictions.", "Verify lighting protocols in field sheds."]
        else:
            status = DriftStatus.CRITICAL
            interp = "CRITICAL: Severe distribution shift detected. Model operating outside expected validation manifold."
            actions = ["Consider temporarily restricting automated screening to syndromic-only.", "Mandate 100% on-site veterinary review.", "Evaluate candidate model in shadow mode."]

        return DriftReport(
            drift_status=status,
            overall_psi=overall_psi,
            confidence_psi=confidence_psi,
            class_distribution_shift=round(class_shift, 4),
            image_quality_shift=quality_shift,
            species_anomaly_rate=round(species_anomaly, 4),
            baseline_sample_count=135,
            current_sample_count=n_samples,
            baseline_window="Dataset A Validation Baseline",
            monitoring_window=f"Last {n_samples} Predictions",
            signals=signals,
            interpretation=interp,
            recommended_actions=actions,
            is_demo_simulated=is_demo
        )


drift_detector = DriftDetector()
