# AniCare AI — 12-Slide National Presentation Deck Outline

**Event:** Smart India Hackathon 2026 Grand Finale  
**Theme:** AI-Powered Animal Health & Disease Early Warning System  
**Presentation Time:** 8–10 Minutes + 5 Minutes Q&A  

---

### Slide 1: Title & National Positioning
- **Title:** AniCare AI
- **Subtitle:** AI-Powered Livestock Health Intelligence, Geospatial Early Warning & Operational Response Platform
- **Tagline:** Detect &bull; Assess &bull; Map &bull; Alert &bull; Investigate &bull; Respond &bull; Monitor
- **Team Details:** Team AniCare AI, SIH 2026 Finalists
- **Key Visual:** System architecture hero graphic with smartphone (farmer), geospatial map (hotspots), and desktop command center (veterinary department).

---

### Slide 2: The National Challenge — 14-Day Information Latency
- **Context:** 300M+ bovine livestock supporting 80M rural dairy households.
- **The Core Problem:** Traditional disease reporting takes 7 to 14 days from village symptom onset to state veterinary notification.
- **The Consequence:** Uncontrolled transmission across talukas, 40% milk yield drops, high cattle mortality, and severe economic losses for smallholder farmers.
- **Root Causes:** Paper reporting, remote geography, zero internet connectivity, fragmented communication between farmers and district veterinarians.

---

### Slide 3: Critical Insight — Why "Just an AI Image Classifier" Fails
- **The Common Flaw:** Building a standalone smartphone image classifier is clinically dangerous and practically ineffective.
  1. *Clinical Ambiguity:* Skin lesions in LSD closely resemble pseudo-lumpy disease, ringworm, and insect stings; visual features alone cannot confirm diagnosis.
  2. *Veterinary Law:* Prescribing antibiotics or vaccines without a registered veterinarian violates Indian statutory regulations and promotes antimicrobial resistance.
  3. *Epidemic Scale:* Individual animal diagnosis does not stop an outbreak without geospatial clustering, cold-chain lab PCR verification, and ring vaccination containment.

---

### Slide 4: The AniCare AI Solution Architecture
- **Layered Architecture Diagram:**
  - *Layer 1:* Low-literacy Farmer Experience (Bilingual Hindi/English, voice input, offline PWA).
  - *Layer 2:* Edge Multimodal Inference (EfficientNet-B0 ONNX + clinical signs fusion).
  - *Layer 3:* Geospatial Intelligence (DBSCAN 5km clustering + spatial risk scoring).
  - *Layer 4:* Department Response Command (P1–P3 alerts, mobile vet dispatch, cold-chain lab custody).
  - *Layer 5:* Continuous AI Governance (PSI drift monitoring, quarantined feedback, frozen weights).

---

### Slide 5: Pillar 1 & 2 — Farmer Usability & Multimodal Risk Fusion
- **Rural Offline Resilience:** IndexedDB client cache with UUIDv4 idempotency prevents data loss and duplicate entries in zero-connectivity areas.
- **Multimodal AI Risk Fusion:**
  - Evaluates raw image probability through fine-tuned EfficientNet-B0.
  - Mathematically fuses vital signs (rectal temperature $> 39.5^\circ\text{C}$, swollen pre-scapular lymph nodes, mucosal ulceration) and vector history.
  - Delivers a calibrated Multimodal Risk Index ($0$ to $100$) rather than an isolated binary guess.

---

### Slide 6: Pillar 3 — Geospatial Outbreak Intelligence & Risk Mapping
- **Spatial Clustering Engine:**
  - Automated DBSCAN ($\varepsilon = 5\text{ km}$, $\text{min\_samples} = 3$) groups concurrent suspected cases.
  - Calculates Spatial Risk Index (SRI) combining case density, disease severity, and infection velocity.
- **Visual Display:** Interactive GeoJSON heatmaps with 5km quarantine buffer zones and block-level vulnerability indices.
- **Early Warning:** Transitions detection from individual animal events to taluka and district-level threat intelligence.

---

### Slide 7: Pillar 4 & 5 — Operational Field Response & Sample Custody
- **Automated Alert Escalation:** Priority P1 Critical, P2 High, and P3 Moderate alerts dispatched to District Veterinary Officer queues.
- **Rapid Response Unit Dispatch:** Mobile vet teams receive on-site digital clinical checklists and farmer advisories.
- **Cold-Chain Biological Sample Custody:** Barcoded custody tracking (`SMP-2026-XXXX`) monitors blood and biopsy specimens under refrigeration from farm gate to diagnostic PCR laboratories.

---

### Slide 8: Human-in-the-Loop Governance & Authorized Department Action
- **Strict Statutory Gatekeeping:**
  - Zero autonomous drug prescribing or automated containment orders.
  - All prescriptions, antibiotics, and containment actions require verified veterinary registration numbers.
- **Triangulated Evidence Dossier:**
  - Chief Veterinary Officer reviews: AI preliminary signal + field clinical findings + definitive lab PCR result.
- **Official Containment Orders:** Directs targeted 5km ring vaccination and movement restrictions.

---

### Slide 9: AI Scientific Validation & Benchmark Metrics
- **Held-Out Test Set Performance ($N = 138$ clinical bovine images, $\tau = 0.50$):**
  - **Accuracy:** 92.75%
  - **Sensitivity (Recall):** 80.95% (17/21 positive cases detected)
  - **Specificity:** 97.92% (94/96 negative controls ruled out)
  - **Precision:** 94.44%
  - **Macro F1 Score:** 0.9106
  - **ROC-AUC:** 0.9452 | **PR-AUC:** 0.9352
- **Calibration Analysis:** Expected Calibration Error (ECE) of 0.1673.

---

### Slide 10: AI Assurance, Drift Monitoring & Dataset Ethics
- **Production Model Invariants:**
  - Binary: `anicare_vision_bovine_v1.onnx` (15.29 MB, SHA-256 verified match).
  - Decision Threshold: Frozen at $\tau = 0.50$.
- **Population Stability Index (PSI):** Current baseline reads **0.04** (healthy, $< 0.10$).
- **Dataset B Quarantine:** External unverified data is strictly quarantined under `PERMISSION_REQUIRED` to preserve ethical data standards and prevent test leakage.
- **Continuous Learning Governance:** Field feedback is quarantined; automated retraining is barred; candidate models undergo 14 days of shadow evaluation.

---

### Slide 11: Live Demonstration Highlights (10-Stage Lifecycle)
- **10-Stage Workflow Walkthrough:**
  1. *Detect* &rarr; 2. *Assess* &rarr; 3. *Map* &rarr; 4. *Alert* &rarr; 5. *Assign* &rarr; 6. *Investigate* &rarr; 7. *Sample* &rarr; 8. *Verify* &rarr; 9. *Decide* &rarr; 10. *Follow-Up*.
- **Pre-Flight Test Verification:** 230 / 230 Automated Pytest Tests PASS.
- **Frontend Build Status:** Clean Vite bundle, 0 errors, 1990 modules.

---

### Slide 12: National Impact, Scalability & Roadmap
- **Socio-Economic Impact:** Protects dairy farmer livelihood, minimizes antimicrobial resistance, prevents milk production collapse.
- **Department Scalability:** Seamless integration with existing Animal Disease Surveillance (NADRS) and INAPH frameworks.
- **Roadmap:**
  - Phase 1: Taluka-level pilot in Anand District, Gujarat.
  - Phase 2: State-wide expansion across cooperative dairy networks (e.g., AMUL federation).
  - Phase 3: National integration with Department of Animal Husbandry & Dairying (DAHD).
- **Closing Statement:** *"AniCare AI transforms fragmented field observations into decisive national disease prevention."*
