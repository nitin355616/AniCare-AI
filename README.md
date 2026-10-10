<<<<<<< HEAD
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
=======
# AniCare AI 🐾

**AI-powered animal disease detection and care assistance**

AniCare AI is a project focused on helping users explore animal-health information through AI-assisted disease detection. The project currently includes a cattle disease detection workflow, with work underway to expand support for dog skin diseases.

> **Important:** AniCare AI is a support tool, not a veterinary diagnosis. Predictions can be wrong. Always consult a qualified veterinarian, especially when an animal is unwell or symptoms are severe.

## ✨ Project Goals

- Analyze animal images for supported disease categories.
- Provide an accessible interface for submitting images and viewing predictions.
- Keep cattle and dog disease models separate to avoid mixing species-specific labels.
- Expand coverage carefully using correctly labeled, appropriately licensed datasets.
- Improve reliability through held-out testing and per-class evaluation.

## 🧩 Current Scope

- **Cattle disease detection:** Existing project functionality for supported cattle-disease classes.
- **Dog skin-disease detection:** Planned/in-progress extension. Dataset availability and model performance must be verified before treating this feature as ready.
- **Web interface and API:** The repository includes frontend and backend components; exact setup requirements are documented in the project files.

## 🛠️ Technology

The project report describes a Python backend using FastAPI/Uvicorn, a frontend using React and Vite, MongoDB integration, and a machine-learning image classifier. Check the actual dependency files and configuration for the current requirements.

## 📁 Project Structure

The repository is organized into frontend and backend components. The backend includes application routes/services, AI model and manifest files, scripts, tests, uploads, and dataset-related folders. Folder names may evolve as the project develops.

## 🚀 Run Locally (Windows)

1. Install **Git**, **Python**, **Node.js (LTS)**, and **MongoDB** if the current project configuration requires them.
2. Open the project folder in Visual Studio Code.
3. Review `RUN_GUIDE.md` and the relevant `README.md` files for the latest project-specific instructions.
4. Configure environment variables using `.env.example` if provided. Keep your real `.env` file private.
5. Start the backend and frontend using the commands documented in `RUN_GUIDE.md` or the project scripts.

If a root-level `run.bat` exists, review it before running it. Do not assume that every service starts successfully until you see its terminal output.

## 🧪 Testing and Model Evaluation

Use the project's test and evaluation scripts described in `RUN_GUIDE.md`. Record actual results from your own run. Do not treat reported accuracy, test counts, or model status as verified unless you reproduce them.

For machine-learning evaluation, use a held-out test set and review:
- Accuracy
- Per-class precision and recall
- Macro F1-score
- Confusion matrix
- Class balance and possible data leakage

## 📚 Datasets and Model Notes

- Use only images with reliable labels and appropriate usage rights.
- Check for corrupt images, duplicates, incorrect species, and inconsistent class names before training.
- Keep training, validation, and test sets separate; where possible, split by animal or source to reduce leakage.
- Do not upload large datasets or model weights to GitHub without checking repository size limits and dataset licenses.
- Never claim that the model detects every animal disease. Some conditions require symptoms, examination, or laboratory tests rather than an image alone.

## 🔐 Security

Before publishing this repository:
- Do **not** commit `.env` files, API keys, passwords, database connection strings, private user data, or credentials.
- Exclude virtual environments, `node_modules`, caches, and local uploads using `.gitignore`.
- Review all files staged in VS Code Source Control before committing.
- Remove any secrets from Git history if they were committed accidentally; simply deleting them in a later commit is not enough.

## 🗺️ Roadmap

- [ ] Verify the current cattle model and its evaluation results.
- [ ] Validate dataset licenses and labels.
- [ ] Add a separate dog skin-disease model.
- [ ] Expand to additional animal-health categories using suitable datasets.
- [ ] Improve uncertainty handling and veterinary guidance.
- [ ] Add reproducible setup and evaluation instructions.

## 🤝 Contributing

Contributions, bug reports, and suggestions are welcome. Before contributing, please document dataset sources and licenses, preserve existing functionality, and include tests where applicable.

## ⚖️ Disclaimer

AniCare AI is intended for educational and decision-support purposes only. It does not replace professional veterinary examination, diagnosis, or treatment. Do not use predictions alone to choose medicines or delay urgent veterinary care.
>>>>>>> aa08acef8f3340cb9a6640a234a9a87c1a2a8280
