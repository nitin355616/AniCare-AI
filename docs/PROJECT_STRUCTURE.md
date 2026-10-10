# AniCare AI — Complete Project Codebase Map

**Repository Root:** `D:\AniCare-AI`  
**Version:** 1.14.0 (Milestone 14 Final Release)  
**Stack:** FastAPI, Python 3.12, ONNX Runtime, MongoDB, React 18, Vite, Tailwind CSS, Pytest  

---

## 1. Top-Level Directory Layout

```text
D:\AniCare-AI/
├── backend/                  # FastAPI Backend, AI Pipelines, Models & Tests
│   ├── ai/                   # AI Training, ONNX Inference & Evaluation
│   │   ├── inference/        # ONNX Runtime inference wrapper
│   │   ├── models/           # ONNX weights & Milestone reports
│   │   │   ├── weights/      # anicare_vision_bovine_v1.onnx (15.29 MB)
│   │   │   └── ...           # Milestone 1 to 14 markdown evaluation reports
│   │   └── training/         # Dataset preprocessing & benchmark scripts
│   ├── app/                  # FastAPI Web Application Core
│   │   ├── core/             # Application configuration & security settings
│   │   ├── db/               # MongoDB client & collection references
│   │   ├── routes/           # REST API Route Endpoints
│   │   ├── schemas/          # Pydantic Request & Response Data Models
│   │   ├── services/         # Core Domain Logic Services
│   │   └── main.py           # FastAPI Application Entrypoint
│   └── tests/                # Automated Pytest Suite (230 tests)
│
├── data/                     # Data Stores & Quarantine Repositories
│   ├── external/             # External data storage
│   │   └── dataset_b/        # QUARANTINED (PERMISSION_REQUIRED)
│   └── feedback/             # Isolated field veterinary feedback registry
│
├── docs/                     # SIH 2026 Presentation & Architecture Documentation
│   ├── architecture/         # Technical architecture deep-dive documents
│   ├── SIH_DEMO_SCRIPT.md    # 5-minute timed demo script
│   ├── SIH_ELEVATOR_PITCH.md # 30-second elevator pitch
│   ├── SIH_3_MINUTE_PITCH.md # 3-minute executive pitch
│   ├── SIH_TECHNICAL_PRESENTATION.md # 10-minute technical breakdown
│   ├── SIH_PPT_OUTLINE.md    # 12-slide presentation structure
│   └── PROJECT_STRUCTURE.md  # Comprehensive codebase directory map
│
├── src/                      # React 18 Frontend Application (Vite + Tailwind CSS)
│   ├── assets/               # Static images & icons
│   ├── components/           # Modular Reusable React UI Components
│   │   ├── common/           # Buttons, Badges, Modals, Cards
│   │   ├── detection/        # Image upload & symptom input widgets
│   │   ├── farmer/           # Low-literacy icon triage & voice input
│   │   ├── geospatial/       # Leaflet maps & cluster visualization
│   │   ├── layout/           # Sidebar, Navbar, AppLayout
│   │   └── response/         # Alert queues, investigation boards & sample tables
│   ├── data/                 # Client mock data & constants
│   ├── i18n/                 # Bilingual Hindi/English translation context
│   ├── pages/                # High-Level Page Views & Dashboard Screens
│   │   ├── Dashboard.jsx
│   │   ├── Animals.jsx
│   │   ├── DiseaseDetection.jsx
│   │   ├── HealthReports.jsx
│   │   ├── VeterinaryCare.jsx
│   │   ├── Alerts.jsx
│   │   ├── Analytics.jsx
│   │   ├── OutbreakIntelligence.jsx
│   │   ├── FarmerExperience.jsx
│   │   ├── AIModelMonitoring.jsx
│   │   ├── GeospatialIntelligence.jsx
│   │   ├── ResponseCommandCenter.jsx
│   │   ├── SIHDemo.jsx                  # (Milestone 14 - /sih-demo)
│   │   ├── SIHExecutiveDashboard.jsx    # (Milestone 14 - /sih-dashboard)
│   │   ├── AIValidationDashboard.jsx    # (Milestone 14 - /ai-validation)
│   │   ├── SIHMapping.jsx               # (Milestone 14 - /sih-mapping)
│   │   └── JuryQnA.jsx                  # (Milestone 14 - /jury-qa)
│   ├── services/             # Client API Networking & Offline Storage
│   │   ├── api/              # Axios/Fetch API Clients
│   │   └── offline/          # IndexedDB cache & sync queue engine
│   ├── App.jsx               # React Router DOM configuration
│   └── main.jsx              # React DOM mounting entrypoint
│
├── dist/                     # Production compiled frontend bundle
├── package.json              # Frontend npm dependencies
├── vite.config.js            # Vite build configuration
└── README.md                 # Primary Project Readme & Overview
```

---

## 2. Key Backend Services (`backend/app/services/`)

| File | Purpose |
| :--- | :--- |
| `demo_service.py` | SIH Demo orchestrator: model SHA-256 verification, scenario seed & safe reset |
| `detection_service.py` | EfficientNet-B0 ONNX inference, multimodal risk calculation ($\tau = 0.50$) |
| `geospatial_service.py` | DBSCAN spatial clustering, spatial density scoring, GeoJSON generation |
| `response_service.py` | P1-P3 operational alert dispatch, investigation board, sample tracking, department action authorization |
| `outbreak_service.py` | Epidemiological velocity, R0 projection, block-level alert indicators |
| `farmer_service.py` | Hindi/English quick symptom reporting, voice input conversion, first aid advice |
| `sync_service.py` | Offline-first batch reconciliation, UUID idempotency deduplication |
| `drift_service.py` | Population Stability Index (PSI) calculation, covariate shift surveillance |
| `feedback_service.py` | Quarantined veterinary clinical feedback registry |
| `veterinary_service.py` | Human-in-the-loop review, diagnosis verification, triage approval |
| `treatment_service.py` | Gated prescription guidelines, antibiotic schedule validation |

---

## 3. Test Suites (`backend/tests/`) — 230 / 230 PASS

| Test File | Focus Area | Status |
| :--- | :--- | :--- |
| `test_milestone14_demo.py` | Demo health, seed, reset, 10-stages, model SHA-256, Dataset A/B invariants | 8/8 PASS |
| `test_milestone13_field_response.py` | Operational alerts, mobile assignment, sample custody, department actions | 33/33 PASS |
| `test_milestone12_geospatial.py` | Spatial clustering (DBSCAN), spatial risk index, GeoJSON endpoints | 18/18 PASS |
| `test_milestone11_drift_monitoring.py` | Model drift (PSI), feedback repository, champion-challenger pipeline | 17/17 PASS |
| `test_milestone10_offline_sync.py` | Offline queue, idempotency deduplication, conflict resolution | 25/25 PASS |
| `test_milestone9d_farmer.py` | Hindi/English farmer portal, low-literacy workflows | 16/16 PASS |
| `test_milestone9c_outbreak.py` | Early warning indicators, reproductive rate R0 | 20/20 PASS |
| `test_milestone9b_treatment.py` | Prescription safety, antibiotic resistance prevention | 22/22 PASS |
| `test_milestone9a_veterinary.py` | Veterinary decision support, human clinical review | 20/20 PASS |
| `test_multimodal_risk_fusion.py` | Vision + clinical symptoms Bayesian-inspired risk engine | 18/18 PASS |
| `test_onnx_pipeline.py` | ONNX runtime inference, preprocessing, model binary invariants | 15/15 PASS |
| `test_api_endpoints.py` | Authentication, animals, health reports, analytics | 18/18 PASS |
| **Total Automated Tests** | **Comprehensive Full Regression Suite** | **230 / 230 PASS (100%)** |
