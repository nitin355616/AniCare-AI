# 🐾 AniCare AI — AI-Powered Animal Health & Disease Early Warning System

> **Smart India Hackathon (SIH 2026) National Finals Project**  
> *A privacy-first, human-in-the-loop livestock health intelligence platform that converts animal-level health signals into geospatial early warnings and controlled veterinary/department response workflows.*  
> **Detect &bull; Assess &bull; Map &bull; Alert &bull; Investigate &bull; Respond &bull; Monitor**

---

## 🌟 Executive Summary

India is home to over **300 million cattle and buffaloes**, providing livelihoods to more than **80 million rural households**. Traditional livestock disease reporting suffers from a **7 to 14-day information latency**, resulting in widespread contagion, 40% milk yield collapse, and severe economic losses for dairy farmers.

**AniCare AI** bridges this gap from Day Zero:
1. **Farmer Experience:** Bilingual (Hindi/English), voice-enabled, low-literacy interface working **100% offline** via IndexedDB caching.
2. **Multimodal AI Risk Fusion:** Fine-tuned EfficientNet-B0 ONNX vision backbone fused with clinical vital signs and vector dynamics.
3. **Geospatial Early Warning:** Automated DBSCAN 5km spatial clustering detects emerging village and block-level hotspots.
4. **Field Response Command:** Tiered operational alerts (P1–P3), Rapid Response Unit dispatch, and barcoded cold-chain sample custody.
5. **Human-in-the-Loop Governance:** Strict statutory compliance under the Indian Veterinary Council Act—zero autonomous drug prescriptions.
6. **Continuous AI Assurance:** Population Stability Index (PSI) drift surveillance, frozen production model weights, and ethical dataset quarantine.

---

## 🏆 Verified Benchmarks & System Invariants

| Invariant / Metric | Verified Baseline | Evidence & Location |
| :--- | :--- | :--- |
| **Automated Tests** | **230 / 230 PASS (100%)** | `pytest backend/tests/` |
| **Frontend Build** | **0 Errors, 1990 Modules** | `npm run build` |
| **Model Weights** | `anicare_vision_bovine_v1.onnx` (15.29 MB) | SHA-256: `594d42c7...f4f8d` (Verified) |
| **Decision Threshold** | $\tau = 0.50$ (FROZEN) | Calibrated for optimum clinical sensitivity |
| **Held-Out Test Accuracy** | **92.75%** ($N = 138$) | Held-out Dataset A test benchmark |
| **Held-Out Specificity** | **97.92%** ($94/96$ true negatives) | Prevents false alarms in rural villages |
| **Held-Out Sensitivity** | **80.95%** ($17/21$ true positives) | Multimodal fusion catches borderline cases |
| **Model Drift Index** | **PSI = 0.04** (Stable $< 0.10$) | Automated weekly surveillance window |
| **Dataset B Status** | **QUARANTINED** | `data/external/dataset_b/` (`PERMISSION_REQUIRED`) |

---

## 🚀 Key Modules & Architecture

### 1. SIH Evaluation Suite (Milestone 14)
- **Interactive 10-Stage Walkthrough (`/sih-demo`):** Step-by-step live simulation of the full detection-to-containment lifecycle with auto-play, safe seed, and reset.
- **Executive Pitch Dashboard (`/sih-dashboard`):** Strategic problem-vs-solution comparison and "Why Not Just an AI Classifier" card.
- **AI Scientific Validation (`/ai-validation`):** Held-out metrics ($N=138$), confusion matrix, and calibration analysis.
- **SIH Requirement Matrix (`/sih-mapping`):** Full traceability linking hackathon requirements to code files, APIs, and tests.
- **Jury Q&A Defense Dossier (`/jury-qa`):** Rigorous answers to the 8 critical jury inquiries.

### 2. Operational Platform
- **Disease Detection (`/disease-detection`):** Live ONNX runtime inference, image upload, and multimodal symptom fusion.
- **Geospatial Intelligence (`/geospatial`):** Interactive Leaflet maps, 5km cluster hazard zones, and block risk scores.
- **Response Command Center (`/response`):** P1–P3 alert queues, mobile team assignment, and cold-chain sample custody.
- **Farmer Experience Portal (`/farmer`):** Hindi/English audio triage and offline sync queue.
- **AI Continuous Monitoring (`/ai-monitoring`):** PSI drift metrics and quarantined veterinary feedback.
- **Veterinary Care (`/veterinary`):** Gated clinical review and drug prescription guidelines.

---

## 🛠️ Quick Start & Running the Project

### Prerequisites
- Python 3.12+ (Anaconda or venv)
- Node.js 18+ & npm
- MongoDB 7.0+ (Local or Atlas)

### 1. Start the Backend API
```bash
# Navigate to backend directory
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Run automated test suite (verifies 230/230 tests)
pytest tests/ -v

# Start FastAPI server with live reload
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
API runs at: `http://127.0.0.1:8000`  
Interactive Swagger Docs: `http://127.0.0.1:8000/docs`

### 2. Start the Frontend
```bash
# In the root repository directory
npm install

# Start Vite development server
npm run dev
```
Web App runs at: `http://localhost:5173`

### 3. Build for Production
```bash
npm run build
```

---

## 📚 Documentation Reference

- [5-Minute SIH Demo Script](docs/SIH_DEMO_SCRIPT.md)
- [30-Second Elevator Pitch](docs/SIH_ELEVATOR_PITCH.md)
- [3-Minute Executive Pitch](docs/SIH_3_MINUTE_PITCH.md)
- [10-Minute Technical Presentation](docs/SIH_TECHNICAL_PRESENTATION.md)
- [12-Slide Presentation Deck Outline](docs/SIH_PPT_OUTLINE.md)
- [Project Codebase Structure](docs/PROJECT_STRUCTURE.md)
- [System Architecture Specification](docs/architecture/system-architecture.md)
- [End-to-End Data Flow](docs/architecture/data-flow.md)
- [AI Inference Pipeline](docs/architecture/ai-pipeline.md)
- [Geospatial Clustering Flow](docs/architecture/geospatial-flow.md)
- [Operational Response Workflow](docs/architecture/response-workflow.md)
- [Offline Synchronization Engine](docs/architecture/offline-sync.md)
- [Model Governance & Ethics](docs/architecture/governance-flow.md)

---

## ⚠️ Statutory Safety & Hackathon Disclaimer
AniCare AI strictly operates under human-in-the-loop clinical supervision. AI risk calculations represent diagnostic support signals and do not replace physical clinical diagnosis or issue autonomous medical prescriptions. In evaluation sandbox environments without active SMS/WhatsApp gateway credentials, notifications are logged transparently as `READY — PROVIDER NOT CONFIGURED`.
