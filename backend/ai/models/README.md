# AniCare AI — Dataset & Vision Model Acquisition Protocol
**Smart India Hackathon (SIH 2026) — Epizootic Surveillance Vision Architecture**

> **STATUS: PLANNING & PROTOCOL SPECIFICATION ONLY**  
> In compliance with ethical data governance and SIH 2026 hackathon guidelines, **no unvetted datasets or unverified weights have been scraped or downloaded**. This document outlines the rigorous, peer-reviewable acquisition and evaluation protocol for deploying real deep learning models into AniCare AI.

---

## 1. Required Image Classes

The vision classification model targets clinical and syndromic lesion categories prioritized by the World Organisation for Animal Health (WOAH / OIE) and the Indian Council of Agricultural Research (ICAR):

| Class ID | Target Condition | Clinical Visual Manifestations | Diagnostic Region |
|---|---|---|---|
| `CLASS_01` | **Foot and Mouth Disease (FMD)** | Mucosal vesicles, ruptured stomatitis ulcers, dental pad erosion, coronary band hyperemia, ropy salivation | Oral cavity, muzzle, hooves/feet |
| `CLASS_02` | **Lumpy Skin Disease (LSD)** | Firm, circumscribed cutaneous nodules (2–5 cm), necrotic sitfasts, regional lymphadenopathy | Neck, flanks, perineum, udder |
| `CLASS_03` | **Bovine Respiratory Disease (BRDC)** | Mucopurulent nasal discharge, serous ocular catarrh, tachypneic nostril flaring | Head, muzzle, nostrils, thorax |
| `CLASS_04` | **Bovine Mastitis** | Udder quarter asymmetry, localized erythema, teat canal induration, abnormal milk strippings | Udder, teats, inguinal region |
| `CLASS_05` | **Healthy / Control** | Intact epidermal barrier, clean oral mucosa, clear bilateral nostrils, symmetrical mammary gland | Full body, face, muzzle, udder |

---

## 2. Target Animal Species

Data acquisition is restricted strictly to four primary domestic livestock species critical to India's rural agrarian economy:

1. **Indigenous & Crossbred Cattle (*Bos indicus* / *Bos taurus*)**: Gir, Kankrej, Sahiwal, Red Sindhi, HF cross.
2. **Water Buffalo (*Bubalus bubalis*)**: Murrah, Mehsana, Jaffarabadi, Surti.
3. **Goats (*Capra hircus*)**: Jamnapari, Barbari, Sirohi, Black Bengal.
4. **Sheep (*Ovis aries*)**: Marwari, Deccani, Nellore, Malpura.

*Exclusion criteria*: Equines, canines, felines, wildlife, and non-target species must be rejected during data curation.

---

## 3. Expected Image Quality & Capture Standards

Field images collected by dairy farmers and Para-Veterinary Field Assistants (PFAs) vary significantly in ambient illumination and device optics. The minimum technical standards include:

* **Resolution**: Minimum $640 \times 640$ pixels uncompressed ($224 \times 224$ minimum crop after bounding box extraction).
* **Sensor / Device**: Minimum 8 Megapixel CMOS smartphone camera or handheld inspection camera.
* **Illumination**: Daylight or minimum 300 lux artificial illumination; no extreme flash blowouts that wash out mucosal color.
* **Focus & Motion**: Sharp focus on lesion morphology (macro shots for vesicles/nodules); images with motion blur obscuring dermal texture must be culled.
* **Color Fidelity**: Standard 24-bit sRGB color space without aesthetic filters, tinting, or digital watermarking.

---

## 4. Annotation Requirements & Ground Truth Protocols

* **Gold Standard Diagnostic Verification**: Every positive training sample must be verified through at least one confirmatory test:
  * *FMD*: RT-PCR / Antigen-capture ELISA confirmed by NIHSAD (Bhopal) or ICAR-DFMD.
  * *LSD*: Capripoxvirus real-time PCR or clinical sign-off by a Gazetted Veterinary Officer.
  * *Mastitis*: California Mastitis Test (CMT $\ge 2+$) or microbiological culture.
* **Annotation Format**: 
  * Class-level classification labels in standard Pascal VOC / COCO JSON schema.
  * Secondary bounding box coordinates (`[xmin, ymin, xmax, ymax]`) isolating the anatomical lesion site from shed background clutter.
* **Inter-Annotator Agreement**: Minimum 3 qualified veterinary pathologists per batch; Cohen’s Kappa coefficient $\kappa \ge 0.85$ required for ground truth admission.

---

## 5. Train / Validation / Test Split Strategy

To guarantee generalizability across geographies, data must be partitioned by **farm unit / shed cluster** rather than random shuffling:

| Partition | Proportion | Stratification Criteria | Purpose |
|---|---|---|---|
| **Training** | 70% | Balanced by species, age, and lesion stage | Gradient updates & feature extraction |
| **Validation** | 15% | Distinct farms never seen in training set | Hyperparameter tuning & early stopping |
| **Test (Holdout)** | 15% | Geographically isolated district farms | Final unbiased evaluation benchmark |

---

## 6. License, Regulatory & Ethical Requirements

* **Zero Web Scraping Policy**: Autonomous web crawling or Google Image harvesting is strictly forbidden due to unverified provenance, copyright infringement, and lack of clinical ground truth.
* **Permissible Sources**:
  1. Open-access research repositories under **CC-BY 4.0** or **CC0** (e.g., Mendeley Data, Zenodo, Dryad, Figshare with verified veterinary attribution).
  2. Institutional collaboration datasets with written MoUs from Veterinary Universities (e.g., AAU Anand, TANUVAS, GADVASU, NDRI).
* **Animal Welfare Compliance**: Only non-invasive diagnostic photography during routine clinical rounds; zero invasive experimental inductions.

---

## 7. Data Leakage Prevention

* **Animal-Level Separation**: Photographs of the same animal taken from multiple angles or consecutive days must **never** be split across train and test sets. All images of a given RFID ear tag must reside exclusively within one split.
* **Farm / Environmental Bias Mitigation**: Background cues (distinctive shed wall paint, ear tag serials, feeder trough design) must not become predictive shortcuts. Background randomization and foreground lesion bounding-box crops must be applied.

---

## 8. Class Imbalance Handling

Notifiable diseases (such as FMD outbreaks) occur in episodic clusters and will be heavily outnumbered by healthy baseline cattle:

1. **Focal Loss Objective**: Implement $\gamma = 2.0$, $\alpha = 0.25$ to heavily downweight easy negative / healthy examples and focus gradient updates on hard borderline lesions.
2. **Stratified Mini-Batch Sampling**: Weighted Random Sampler ensuring every mini-batch contains a balanced 1:1:1:1:1 representation of all 5 target classes.
3. **Class-Weighted Cross-Entropy**: Penalize false negatives on critical classes proportionally to their inverse frequency.

---

## 9. Data Augmentation Protocol

Augmentations must preserve biological plausibility:

* **Permissible Augmentations**:
  * Random Horizontal Flip ($p = 0.5$).
  * Random Rotation ($-15^\circ$ to $+15^\circ$).
  * Subtle Color Jitter (Brightness $\pm 10\%$, Contrast $\pm 10\%$, Saturation $\pm 8\%$).
  * Random Affine Translation & Scale ($\pm 8\%$).
* **Prohibited Augmentations**:
  * Vertical Flips (animals do not stand upside-down).
  * Extreme Hue Distortion (altering mucosal redness alters inflammation grade).
  * Aggressive CutMix/Mosaic (creates anatomically impossible chimeric livestock).

---

## 10. Evaluation Strategy & Metrics

For a national-level biosecurity early-warning platform, **false negatives on high-risk notifiable diseases carry catastrophic economic consequences**:

$$\text{Sensitivity / Recall (High Risk)} = \frac{TP}{TP + FN} \quad \text{[Target: } \ge 95.0\% \text{]}$$

1. **Primary Metrics**:
   * **Per-Class Recall**: Minimum $95\%$ recall required on FMD and LSD.
   * **Macro F1-Score**: Harmonic mean across all 5 classes to balance precision and recall.
   * **Confusion Matrix Analysis**: Explicit tracking of off-diagonal misclassifications.
2. **Secondary Metrics**:
   * Area Under ROC Curve (AUROC) $\ge 0.96$ per class.
   * Latency on single CPU core $\le 85\text{ ms}$ (MobileNetV3 quantized ONNX runtime).
