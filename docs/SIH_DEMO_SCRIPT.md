# AniCare AI — 5-Minute SIH National Jury Demo Script

**Project Title:** AniCare AI — AI-Powered Animal Health & Disease Early Warning System  
**Hackathon:** Smart India Hackathon (SIH) 2026 National Finals  
**Demonstration Mode:** Live Interactive Walkthrough (`/sih-demo`)  
**Core Positioning Statement:**  
> *"AniCare AI is a privacy-first, human-in-the-loop livestock health intelligence platform that converts animal-level health signals into geospatial early warnings and controlled veterinary/department response workflows."*  
> *(Detect &bull; Assess &bull; Map &bull; Alert &bull; Investigate &bull; Respond &bull; Monitor)*

---

## Pre-Flight Check (0:00 - 0:15)
- Open browser to `http://localhost:5173/sih-demo`
- Ensure backend server is healthy (`/api/demo/health` returns 200 OK)
- Point to the **System Invariants Bar**:
  - Model: `anicare_vision_bovine_v1.onnx` (SHA-256 verified)
  - Threshold: $\tau = 0.50$ (Frozen)
  - Dataset A Test Benchmark: $92.75\%$ Accuracy, $0.9452$ ROC-AUC ($N=138$)
  - Dataset B Status: `QUARANTINED (PERMISSION_REQUIRED)`
  - Automated Tests: `230/230 PASS` (100%)

---

## 5-Minute Script Breakdown

### Minute 0:15 – 0:45 | Hook & Core Problem
**Presenter:**
> "Respected Jury Members, India has over 300 million bovine livestock supporting 80 million rural families. When an infectious disease like Lumpy Skin Disease or Foot-and-Mouth Disease strikes, the traditional system takes 7 to 14 days to detect and escalate. By then, whole blocks are infected, milk output crashes by 40%, and farmers lose their livelihoods.
>
> Many teams build an image classification mobile app and call it solved. But in reality, an isolated AI model is clinically dangerous and administratively useless: skin lesions mimic multiple conditions, AI cannot legally prescribe drugs, and a single diagnosis doesn't stop an epidemic.
>
> That is why we built **AniCare AI**: not just a classifier, but an end-to-end national early warning and operational field response platform. Today, we will demonstrate the entire 10-stage lifecycle live in under 5 minutes."

---

### Minute 0:45 – 1:30 | Stage 1 & 2: Signal Detection & Multimodal Risk Fusion
**Action:** Click **"Seed SIH Live Scenario"**, then click **Stage 1 (DETECT)**.
**Presenter:**
> "Stage 1 begins in Anand Village, Gujarat. Farmer Ramesh reports a sick cow with circular nodular skin lesions and lethargy.
> Notice our Farmer Experience Portal: it is bilingual in Hindi and English, uses visual icon triage, voice inputs, and works completely offline using IndexedDB caching. Even with zero mobile signal in remote pasturelands, zero data is lost.
>
> Moving to **Stage 2 (ASSESS)**:
> Here is where our AI inference pipeline acts. The EfficientNet-B0 ONNX production model evaluates the lesion image, predicting 88.4% visual probability.
> But AniCare never diagnoses on vision alone. Our Multimodal Risk Fusion engine integrates the rectal temperature of 40.5°C, swollen pre-scapular lymph nodes, and regional vector activity into a calibrated Multimodal Risk Index of 83 out of 100.
> **Our first safety invariant:** The AI produces a decision-support signal, never an autonomous prescription."

---

### Minute 1:30 – 2:30 | Stage 3 & 4: Geospatial Early Warning & Operational Alerts
**Action:** Click **Stage 3 (MAP)**, then click **"Open /geospatial"** to show the live map.
**Presenter:**
> "Stage 3 is what transforms AniCare into an institutional early warning system.
> As 3 other farmers in neighboring hamlets report similar symptoms within a 5 km radius, our geospatial engine automatically executes DBSCAN density clustering.
> Rather than isolated cases, it identifies an active cluster in Anand Rural Block with a Spatial Risk Index of 86.0 and an infected cluster radius of 4.2 km.
>
> In **Stage 4 (ALERT)**:
> The system deduplicates these events and generates a Priority P1 Operational Alert on the District Veterinary Officer's dashboard.
> **Note our operational transparency:** Notice that SMS and WhatsApp notifications are clearly tagged as `READY — PROVIDER NOT CONFIGURED`. We never fabricate fake telecom carrier delivery."

---

### Minute 2:30 – 3:30 | Stage 5 to 7: Field Mobile Unit, Physical Clinical Exam & Cold-Chain Sample Custody
**Action:** Click **Stage 5 (ASSIGN)**, then advance through **Stage 6 (INVESTIGATE)** and **Stage 7 (SAMPLE)**.
**Presenter:**
> "Now the response shifts to qualified human authority.
> In Stage 5, the District Veterinary Officer assigns Mobile Response Unit #4 led by Dr. Rajesh Verma.
>
> In Stage 6, Dr. Verma visits the village, conducts a formal physical examination, enters vital parameters, confirms clinical presentation consistent with LSD, and advises the farmer on immediate supportive isolation.
>
> In Stage 7, Dr. Verma collects biological specimens: a skin nodule biopsy and EDTA whole blood. Look at our custody tracker: Sample `SMP-2026-0802` is assigned a unique barcode and tracked under cold-chain refrigeration from the farm gate to the District Diagnostic Laboratory. Tamper-evident custody is maintained at every handoff."

---

### Minute 3:30 – 4:15 | Stage 8 & 9: Lab PCR Confirmation & Authorized Department Action
**Action:** Click **Stage 8 (VERIFY)**, then advance to **Stage 9 (DECIDE)**.
**Presenter:**
> "In Stage 8, the state diagnostic lab inputs the confirmatory PCR test result: Capripoxvirus DNA Positive.
> The Chief Veterinary Officer now has a complete triangulated dossier: AI preliminary signal + field clinical examination + definitive molecular PCR validation.
>
> In Stage 9, the Chief Veterinary Officer digitally authorizes official containment Directive `AUTH-2026-001`:
> 1. A 5 km ring vaccination deploying 1,200 goat pox vaccine doses.
> 2. Livestock movement restriction within the containment zone.
> 3. Vector fumigation spray teams deployed.
> **Notice our human governance invariant:** Official containment orders and prescription regimes strictly require certified veterinary signatures."

---

### Minute 4:15 – 4:45 | Stage 10: Follow-Up & Continuous AI Model Drift Monitoring
**Action:** Click **Stage 10 (FOLLOW-UP)**, then click **"Open /ai-monitoring"**.
**Presenter:**
> "Stage 10 closes the loop. Over the subsequent 21 days, mobile units track herd recovery, confirming zero active cases.
> Simultaneously, the verified clinical case is fed into our continuous AI monitoring pipeline.
> Look at our Population Stability Index (PSI): it currently reads 0.04, indicating healthy distribution stability well below the 0.10 drift threshold.
> Most importantly: **the production ONNX weights remain strictly frozen**. Verified field feedback is curated in an isolated registry. Any candidate challenger model must undergo 14 days of shadow evaluation before human ML engineers approve promotion."

---

### Minute 4:45 – 5:00 | Conclusion & Defense Ready
**Presenter:**
> "To summarize:
> - **We have 230 out of 230 automated regression tests passing.**
> - **Our held-out benchmark is 92.75% accurate with 97.92% specificity on N=138 real clinical bovine images.**
> - **External Dataset B is strictly quarantined under permission-required governance.**
> - **Every requirement of the SIH Problem Statement is implemented, tested, and live.**
>
> AniCare AI is ready for deployment across India's animal husbandry departments. We are open for jury questions."
