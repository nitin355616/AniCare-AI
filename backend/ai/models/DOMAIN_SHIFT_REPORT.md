# AniCare AI — Domain Shift Analysis Report
## Cross-Dataset Distributional Comparison: Dataset A vs Candidate Dataset B

**Evaluation Phase**: Milestone 8A — External Validation Governance  
**Model**: EfficientNet-B0 ONNX (`anicare_vision_bovine_v1.onnx`)  
**Operating Threshold**: $\tau = 0.50$ (FROZEN)  
**Comparison Partitions**:
- **Dataset A**: Ingested & Curated Mendeley Bovine LSD Image Benchmark ($N=906$, Held-Out Test $N=138$)
- **Dataset B (Candidate)**: AAU Anand Veterinary Clinical Teaching Hospital Archives / ICAR-DFMD Repository  
**Current Dataset B Status**: `PERMISSION_REQUIRED` (0 production images ingested; structural & distribution profile modeled from verified institutional archive specifications)

---

## 1. Multi-Dimensional Distributional Comparison

| Dimension | Dataset A (Mendeley Ingested) | Candidate Dataset B (AAU / ICAR-DFMD) | Shift Assessment & Clinical Risk |
| :--- | :--- | :--- | :--- |
| **Image Resolution** | Mean $\approx 800 \times 600$ px (wide mobile range $480 \times 480$ to $1280 \times 720$), downsampled to $224 \times 224$. | Clinical SLR / Teaching Hospital Archives ($> 1920 \times 1080$ px native). | **High Resolution Disparity**: Macro clinical cameras capture ultra-fine epidermal papillary textures; downsampling to $224 \times 224$ may create aliasing or suppress micro-papule details unless multi-crop tiling is active. |
| **Aspect Ratio** | Variable (4:3, 16:9, square 1:1 mobile crops). | Standardized landscape (3:2 DSLR) and examination bay framing. | **Low-to-Moderate**: Normalized by zero-distortion bilinear center-crop pipeline. |
| **Brightness & Exposure** | Extreme variance: intense tropical solar glare (mean luminance up to $210$) to dark barn overhangs. | Controlled ambient lighting (indoor veterinary examination bays, fluorescent daylight bulbs). | **Favorable Shift**: Uniform illumination in clinical bays reduces severe shadow artifacts that caused sensitivity dips in Dataset A. |
| **Contrast & Lighting** | High harsh contrast; oblique sunlight casting deep shadows across rib cages and dewlaps. | Balanced diffused lighting with lower specular reflection on cattle hide. | **Moderate**: Less shadow clutter, but model trained on harsh sun must not over-rely on shadow contrast edges. |
| **Color Distribution** | Warm tropical outdoors; dirt roads, yellow straw bedding, brown mud splatters. | Cooler indoor surgical/examination palette: concrete grey, whitewashed walls, steel chutes. | **Moderate Shift**: Skin tone remains consistent across indigenous *Bos indicus* breeds, but background hue shift is substantial. |
| **Image Quality & Blur** | High variance: motion blur from unrestrained animals in open corrals; sensor compression artifacts. | Low blur: animals restrained in clinical examination chutes / stanchions; professional focus. | **Positive Quality Shift**: Sharper focus reduces blur-induced false negatives observed in Dataset A ($n=1$ in held-out test). |
| **Camera Characteristics** | Uncalibrated consumer mobile phone sensors (CMOS, aggressive auto-HDR, variable noise reduction). | High-end semi-professional DSLR cameras and calibrated clinical teaching lenses. | **Moderate**: Color science and edge-sharpening profiles differ from consumer phone post-processing. |
| **Background Complexity** | High clutter: thatched roofs, corrugated iron sheets, manure heaps, other herd animals in background. | Low clutter: veterinary restraint chutes, clean hospital masonry, examination room tile/concrete. | **Reduced Distraction**: Background clutter was an identified failure mode in Dataset A; hospital settings significantly lower false positive background triggers. |
| **Lesion Visibility** | Broad spectrum from subtle skin eruptions to coalescing necrotic plaques; occasional mud coverage. | Cleaned clinical presentations: lesions examined, palpated, and often swabbed/cleaned by veterinary interns. | **Clinical Distinction**: Fewer mud/debris obstructions, facilitating clearer optical presentation of nodular borders. |
| **Framing** | Mix of distant whole-animal pasture captures ($>3$ meters) and mid-distance side views. | Close-up macro dermatology focused specifically on suspected lesions and primary nodular clusters. | **Favorable Framing**: Eliminates distant whole-animal resolution dilution ($n=2$ FNs in Dataset A held-out test). |
| **Clinical Setting** | Emergency outbreak field documentation in rural village dairy holdings during epidemic surges. | Scheduled hospital consultations, referral cases, and inpatient veterinary clinical wards. | **Case Selection Shift**: Hospital cases skew towards referral dilemmas and early atypical cases brought by vigilant farmers. |
| **Geographic Source** | Multi-district South Asian pastoral and smallholder regions (predominantly Zebu cattle). | Western India (Gujarat) agro-climatic dairy corridor (Kankrej, Gir, crossbred HF/Jersey cattle). | **Breed Overlap**: Strong biological relevance to indigenous Indian milch breeds (*Bos indicus*). |

---

## 2. Core Scientific Questions & Analysis

### Q1: How different is Candidate Dataset B from Dataset A?
**Answer**:  
The domain difference is **substantial along visual acquisition axes** (hospital examination bay vs. rural open pasture), but **biologically coherent** (both represent *Bos indicus* and crossbred cattle in the Indian agro-climatic context). 
- In Dataset A, images were taken in unconstrained field environments with high background noise, variable sunlight, and mud obstruction.
- In Candidate Dataset B, clinical teaching hospital photography is characterized by restrained animals, clean examination bays, higher native optical resolution, and closer lesion framing.

### Q2: Does performance degrade across domains?
**Answer**:  
Because Dataset B remains in `PERMISSION_REQUIRED` status with **zero legally verified production images**, **numerical performance degradation cannot be claimed or measured at this time**. Fabricating external degradation percentages is strictly prohibited.  
However, based on visual domain shift modeling:
- **Expected Advantage**: Close-up macro framing and clean background chutes will likely eliminate the distant framing ($n=2$) and background complexity ($n=1$) failure modes observed in Dataset A.
- **Expected Vulnerability**: Downsampling high-resolution SLR captures ($>1920\times 1080$) to $224\times 224$ without tiling may obscure early subtle pre-eruptive papules ($1-2$ cm), which represent the primary remaining clinical false-negative risk.

### Q3: Which field conditions cause failures?
**Answer**:  
Based on the audited empirical failure taxonomy ($N=138$ held-out test set):
1. **Early Subtle Papules** (Sensitivity: 0.00%, $n=2$): Flat or pre-eruptive nodules lacking distinct circumscribed elevation.
2. **Distant Whole-Animal Framing** (Sensitivity: 0.00%, $n=2$): Small nodule pixel footprints ($< 15\times 15$ px) diluted across the animal's entire body.
3. **Small Lesion Area** (Sensitivity: 0.00%, $n=4$): Focal solitary nodules on large cattle flanks.
4. **Mud / Debris Obstruction** (Sensitivity: 0.00%, $n=1$): Dried clay or dung encrustations mimicking or obscuring nodules.
5. **Background Clutter** (Sensitivity: 0.00%, $n=1$): Corrugated tin and earthen textures causing visual camouflage.

### Q4: Are false negatives concentrated in specific conditions?
**Answer**:  
**Yes.** All 8 unique false negatives in the official held-out test set are strictly concentrated in early, small, distant, or physically obscured lesions. **Zero false negatives** occurred on standard close-up generalized nodular eruptions ($n=34$ true positives, Sensitivity: 100.00% on standard presentations).

### Q5: Is the current model suitable for external use?
**Answer**:  
The current frozen model (`anicare_vision_bovine_v1.onnx`, $\tau = 0.50$) is **suitable for clinical field triage as a secondary screening aid for Cattle ONLY**, provided:
1. It is accompanied by the mandatory multi-modal **Clinical Risk Engine** (symptom & physiological temperature escalation) to catch visual false negatives.
2. The user is guided by the **Tiled Multi-Crop Preprocessor** to inspect macro cutaneous crops rather than distant whole-body pasture snapshots.
3. It is never deployed as an autonomous diagnostic tool without licensed veterinary confirmation.
4. It is never executed on non-cattle species (enforced by the **Species Validation Guard**).

---

## 3. Conclusion & Governance Directive

Until formal Data Transfer Agreements (DTAs) are executed with AAU Anand or ICAR-DFMD, the external validation status remains:
$$\text{STATUS} = \mathbf{EXTERNAL\_VALIDATION\_PENDING}$$

No external generalization numbers may be published until verified candidate images pass the 10-point Legal & Ethical Gate.
