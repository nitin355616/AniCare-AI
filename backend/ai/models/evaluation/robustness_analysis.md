# AniCare AI — Data Augmentation & Multi-Crop Robustness Benchmark

**Milestone**: Milestone 6 — High-Resolution & Multi-Crop Inference  
**Validation Partition**: 135 Images (40 LSD, 95 Healthy / Normal)  

---

## 1. Multi-Crop & Spatial Tiling Architecture

To address distant whole-animal framing where nodules occupy $<5\%$ of total pixels, AniCare AI evaluated a 5-patch multi-scale spatial decomposition:
1. **Global View**: Entire animal field-of-view resized to $224 \times 224$.
2. **Center Zoom (1.25x)**: Central crop capturing core thoracic and neck region.
3. **Four Overlapping Quadrants**: Top-Left, Top-Right, Bottom-Left, Bottom-Right with 20% spatial overlap.

Aggregation formula: $p_{\text{final}} = (0.60 \times p_{\text{global}}) + (0.40 \times p_{\text{max\_patch}})$.

---

## 2. Validation Benchmark Comparison Table

| Pipeline Mode | Input Strategy | Val LSD Recall | Val Specificity | Val Macro F1 | Val FNs | Avg CPU Latency | Feasibility Status |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **Baseline Global** | Single 224x224 | **92.50%** | **95.79%** | **0.9383** | 3 | **24.23 ms** | **DEFAULT (Edge SLA)** |
| **Multi-Crop Tiled** | 5 Patches Ensemble | **95.00%** | 84.21% | **0.8606** | 2 | 98.55 ms | **OPTIONAL HIGH-PRECISION** |

---

## 3. Engineering Analysis & Latency Trade-off

- **Latency Impact**: Multi-crop inference increases processing time from `24.23 ms` to `98.55 ms` (a **4.07x computational overhead**).
- **Deployment Recommendation**: For edge farm deployment and real-time mobile uploads ($<200\text{ ms}$ budget), the single-crop global inference remains the default engine. Multi-crop tiled inference is integrated into `TiledPreprocessor` as an optional parameter for high-precision veterinary secondary screening.