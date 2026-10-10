# AniCare AI — Run Guide & System Manual

**Smart India Hackathon (SIH 2026)**  
**Architecture:** FastAPI Backend (Asynchronous) + React 18 / Vite Frontend + PyTorch 2.14 / ONNX Vision Engines  
**Environment:** Windows (x64) | Python 3.14.8 | Node.js / Vite 5  

---

## 1. Environment & Prerequisites

* **Operating System:** Windows 10 / 11 / Server
* **Python Environment:** Existing virtual environment at `D:\AniCare-AI\backend\.venv` (Python 3.14.8)
* **Node.js:** Node.js 18+ with `npm` installed
* **Database:** MongoDB running locally on `mongodb://127.0.0.1:27017` (database name: `anicare_ai`)

All required Python dependencies (`torch`, `torchvision`, `onnxruntime`, `fastapi`, `motor`, `pillow`, `scikit-learn`, `pytest`, `uvicorn`) are already installed in `backend\.venv`.

---

## 2. Configuration (`.env`)

The project uses two configuration files (both already created with sensible defaults):

1. **Backend Configuration:** `D:\AniCare-AI\backend\.env`
   ```env
   PROJECT_NAME="AniCare AI — Animal Health & Early-Warning Platform"
   ENVIRONMENT="development"
   DEBUG=true
   MONGODB_URL="mongodb://127.0.0.1:27017"
   DATABASE_NAME="anicare_ai"
   JWT_SECRET_KEY="anicare_ai_jwt_super_secret_key_sih2026_dev_seed"
   UPLOAD_DIR="uploads"
   MAX_UPLOAD_SIZE_MB=10
   CORS_ORIGINS="http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000"
   ```

2. **Frontend Configuration:** `D:\AniCare-AI\.env`
   ```env
   VITE_API_BASE_URL=http://127.0.0.1:8000/api
   VITE_APP_ENV=development
   ```

---

## 3. Quick Startup (One-Click)

From the project root (`D:\AniCare-AI`), execute:

```cmd
run.bat
```

This launches both the FastAPI backend (`http://127.0.0.1:8000`) and the Vite React frontend (`http://localhost:5173`) in dedicated command windows.

---

## 4. Manual Service Startup Commands

### Start Backend Only:
```cmd
cd /d D:\AniCare-AI\backend
.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```
Or via script:
```cmd
run.bat backend
```

### Start Frontend Only:
```cmd
cd /d D:\AniCare-AI
npm run dev
```
Or via script:
```cmd
run.bat frontend
```

---

## 5. Dataset Inspection & Manifest Generation

The dataset audit pipeline scans all 5 local datasets, excludes corrupt/backup files and non-bovine species (such as swine/pig FMD images in the cattle folder), prevents duplicate leakage across splits, and builds reproducible cryptographic manifests:

```cmd
run.bat manifests
```
*Direct command:*
```cmd
cd /d D:\AniCare-AI\backend
.venv\Scripts\python.exe scripts\generate_dataset_manifests.py
```

### Verified Dataset Summary:
* **Task A (Cattle Disease):** 3,565 eligible bovine images across 3 verified classes:
  * Healthy / Normal: 1,464
  * Foot and Mouth Disease (FMD): 895 (19 swine/pig lesion photos cleanly excluded)
  * Lumpy Skin Disease (LSD): 1,206
  * Excluded/Quarantined: 57 (38 `.jpg~` backup files + 19 swine photos)
  * Splits: 2,491 train / 532 val / 536 held-out test (leakage-resistant)
* **Task B (Species Guard):** 900 images across Cattle (150), Dog (150), Cat (150), Bird (450)
* **Task C (Muzzle Biometrics):** 1,176 images across 77 distinct bovine muzzle print profiles (non-clinical identification only)
* **Excluded Partition:** 12,500 unlabelled Kaggle pet photos in `External_Test_Data\test` (quarantined)

---

## 6. Model Training & Evaluation

### Evaluate Trained Model on Held-Out Test Split (536 images):
```cmd
run.bat eval-model
```
*Direct command:*
```cmd
cd /d D:\AniCare-AI\backend
.venv\Scripts\python.exe scripts\train_disease_classifier.py --eval-only
```
**Measured Test Performance:**
* Accuracy: **92.72%** (497 / 536 correct)
* Macro F1-Score: **0.9266**
* Foot and Mouth Disease Recall: **87.31%** (Precision: 95.90%)
* Lumpy Skin Disease Recall: **95.60%** (Precision: 94.05%)
* Healthy / Normal Recall: **93.64%** (Precision: 89.96%)

### Retrain / Fine-tune Model:
```cmd
run.bat train-model
```
*Direct command:*
```cmd
cd /d D:\AniCare-AI\backend
.venv\Scripts\python.exe scripts\train_disease_classifier.py --epochs 4 --batch-size 32
```

---

## 7. Service Health & API Testing

### Check Health Endpoint:
```cmd
curl -s http://127.0.0.1:8000/api/health
```
Response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "project_name": "AniCare AI — Animal Health & Early-Warning Platform",
  "environment": "development",
  "database": {
    "connected": true,
    "database": "anicare_ai",
    "latency_ms": 0.88
  },
  "demo_inference_mode": true
}
```

### Check Models Status:
```cmd
curl -s http://127.0.0.1:8000/api/models/status
```

### Run Automated Test Suite (250 Tests):
```cmd
run.bat test
```
*Direct command:*
```cmd
cd /d D:\AniCare-AI
backend\.venv\Scripts\python.exe -m pytest backend/tests -v
```

---

## 8. Test an Image Prediction End-to-End

### Upload an Image:
```cmd
curl -X POST -F "file=@D:\AniCare-AI\backend\datasets\FMD_Cattle\FMD_Cattle\1\Diseased tongue 1.jpg" http://127.0.0.1:8000/api/detection/upload
```
Returns:
```json
{
  "image_id": "IMG-XXXXXXXXXXXX",
  "url": "/uploads/IMG-XXXXXXXXXXXX.jpg"
}
```

### Run Real Neural Disease Prediction:
```cmd
curl -X POST -H "Content-Type: application/json" -d "{\"image_id\": \"IMG-XXXXXXXXXXXX\"}" http://127.0.0.1:8000/api/detection/predict-real
```
Or test directly on a verified dataset sample:
```cmd
curl -X POST -H "Content-Type: application/json" -d "{\"image_id\": \"disease_00200\"}" http://127.0.0.1:8000/api/detection/predict-real
```

---

## 9. Veterinary Safety & Clinical Disclaimer

1. **Screening Prototype:** AniCare AI is an assistive decision-support triage prototype. It does NOT replace on-site physical clinical examination or laboratory assays (RT-PCR, ELISA) by a certified veterinary officer.
2. **Prescription Guard:** The system does NOT prescribe medicines, antibiotics, or dosages autonomously.
3. **Contagious Biosecurity Precautions:** When FMD or LSD is detected, the API returns immediate non-pharmaceutical biosecurity isolation and disinfection recommendations (quarantine, 4% sodium carbonate disinfection, block veterinary notification).

---

## 10. Known Limitations

* **Species Scope:** Disease classification models are trained exclusively on bovine cattle (*Bos taurus* / *Bos indicus*). Non-bovine species photos (swine, avian, canine, feline) are routed through the Species Guardrail.
* **External Dataset Quarantine:** `External_Test_Data` contains unlabelled Kaggle domestic animal images and is strictly quarantined from disease training.
* **Muzzle Biometrics:** Muzzle photographs in `Sahiwal_Cattle_Murrah_Buffalo` are indexed exclusively for individual biometric identification, not disease diagnosis.
