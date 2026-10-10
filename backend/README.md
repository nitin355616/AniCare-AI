# AniCare AI — Backend Service Architecture
**Smart India Hackathon (SIH 2026) — National Hackathon Prototyping Engine**

AniCare AI provides a high-performance, asynchronous REST API backend engineered with **Python 3.12**, **FastAPI**, **MongoDB** (via async `motor`), and **Pydantic v2**. It powers real-time animal surveillance, biosecurity outbreak alerts, and clinical workflows for livestock health-tech.

---

## 🏛️ System Architecture

```text
backend/
├── app/
│   ├── config.py              # Pydantic BaseSettings with .env management
│   ├── database.py            # Async Motor connection pool & collection accessors
│   ├── main.py                # FastAPI lifecycle, CORS, static mounts, and routes
│   ├── middleware/
│   │   ├── __init__.py
│   │   └── error_handler.py   # Uniform JSON exception handlers (422, 500, etc.)
│   ├── models/                # Database collection schemas
│   ├── routes/                # Modular REST API endpoints
│   │   ├── alerts.py          # Biosecurity early warnings & acknowledgments
│   │   ├── animals.py         # Livestock registry CRUD & telemetry
│   │   ├── auth.py            # User registration, login, and JWT /me profile
│   │   ├── detection.py       # Safe photo upload & Demo AI inference
│   │   ├── health.py          # /api/health with live MongoDB ping
│   │   ├── health_records.py  # Clinical telemetry & longitudinal history
│   │   └── veterinary.py      # Case reviews & certified prescription workflows
│   ├── schemas/               # Type-safe Pydantic v2 schemas
│   │   ├── alert.py
│   │   ├── animal.py
│   │   ├── auth.py
│   │   ├── common.py
│   │   ├── detection.py
│   │   ├── health_record.py
│   │   └── veterinary.py
│   ├── services/              # Business logic & simulation engines
│   │   ├── alert_service.py
│   │   ├── animal_service.py
│   │   ├── auth_service.py
│   │   ├── detection_service.py # DemoInferenceEngine (pluggable ML layer)
│   │   ├── health_record_service.py
│   │   └── veterinary_service.py
│   └── utils/
│       ├── file_storage.py    # Non-executable file storage & magic byte validation
│       └── security.py        # Bcrypt salted hashing & PyJWT token handling
├── tests/
│   ├── conftest.py            # Pytest session TestClient fixture with lifespan
│   └── test_backend.py        # 9 comprehensive automated test suites
├── uploads/                   # Secured file storage for uploaded animal photos
├── .env.example               # Environment variables template
├── requirements.txt           # Python dependency specifications
└── README.md
```

---

## 🔒 Biosecurity & Medical Guardrails

1. **Pluggable AI Inference Contract (`DEMO_INFERENCE`)**:
   - The `/api/detection/analyze` endpoint routes to `DemoInferenceEngine` in `app/services/detection_service.py`.
   - Returns structured differential diagnoses, confidence values, risk classifications, and immediate actions.
   - Designed as a drop-in adapter: future milestones can replace this class with a PyTorch/ONNX runtime model without altering the schema or API contracts.
   - Includes mandatory disclaimer: AI-assisted assessments are non-autonomous and do not constitute a confirmed prescription without veterinary examination.

2. **Veterinary Prescription Protection**:
   - The `/api/veterinary/cases/{case_id}/treatment` endpoint strictly validates `prescribing_vet_license`.
   - Direct autonomous machine prescriptions are strictly blocked (returns HTTP 400).

3. **Secure Photo Ingestion**:
   - `/api/detection/upload` verifies header magic bytes (`\xff\xd8\xff` for JPEG, `\x89PNG` for PNG, `RIFF` for WEBP).
   - Validates size limit (10MB max).
   - Generates non-guessable UUID filenames (`IMG-XXXXXXXXXXXX.ext`).
   - Stores in a dedicated uploads volume without server execution permissions.

---

## 🗄️ Database Collections (MongoDB)

| Collection | Purpose | Key Indexes |
|---|---|---|
| `users` | User accounts (farmer, veterinarian, admin) | `email` (unique), `username` |
| `animals` | Livestock registry & biometrics | `animal_id` (unique), `tag` (unique), `species`, `health_status` |
| `health_records` | Clinical telemetry & observation records | `animal_id`, `timestamp` |
| `disease_assessments` | AI inference history & differential diagnoses | `assessment_id` (unique), `animal_id` |
| `veterinary_cases` | Veterinary clinical case tracking & treatments | `case_id` (unique), `animal_id`, `case_status` |
| `alerts` | Biosecurity warnings & outbreak clusters | `alert_id` (unique), `severity`, `alert_type`, `created_at` |

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.10+ (tested on Python 3.12)
- MongoDB v6+ running locally on port 27017

### 2. Installation
```bash
# Navigate to backend directory
cd backend

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Setup
```bash
# Copy example environment configuration
copy .env.example .env
```

Ensure MongoDB is running:
```powershell
Get-Service -Name MongoDB
```

### 4. Running the Backend Server
```bash
# Launch FastAPI with Uvicorn
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

- **Interactive Swagger Documentation**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc Documentation**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
- **Health Check Endpoint**: [http://127.0.0.1:8000/api/health](http://127.0.0.1:8000/api/health)

---

## 🧪 Automated Testing

AniCare AI backend includes an end-to-end automated test suite:

```bash
python -m pytest backend/tests -v
```

All 9 test suites verify:
- System discovery and live MongoDB ping latency
- User registration, login, and JWT bearer authentication
- Livestock registry CRUD with search and species filters
- Longitudinal clinical health telemetry recording
- Photo uploads with magic byte security validation
- AI multivariable disease detection simulation (BRD, FMD, LSD, Mastitis)
- Veterinary review and prescription license guards
- Biosecurity outbreak alert dispatch and acknowledgment
