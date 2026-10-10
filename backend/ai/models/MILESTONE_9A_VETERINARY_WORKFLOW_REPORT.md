# AniCare AI — Milestone 9A Technical Report
## Veterinary Decision Support Workflow & Clinical Lifecycle Governance

---

### 1. Objective
The primary objective of Milestone 9A is the implementation of an end-to-end, clinically governed **Veterinary Decision Support Workflow MVP** for the **AniCare AI — AI-Powered Animal Health & Disease Early Warning System** (SIH 2026). The workflow bridges autonomous AI screening / telemetry triage with certified Veterinary Medical Officer oversight, ensuring that no machine learning prediction is ever treated as an autonomous or final medical diagnosis. All clinical reviews, pharmaceutical prescriptions, follow-up examinations, and case discharges are strictly governed, role-authorized, audit-logged, and persisted directly to the active MongoDB database (`anicare_ai.veterinary_cases`).

---

### 2. Existing Architecture Preserved
The implementation preserved all existing architectural foundations with 100% backward compatibility and zero regression:
- **Vision Model Weights & Configuration**: The production EfficientNet-B0 ONNX model (`anicare_vision_bovine_v1.onnx`), frozen operating threshold ($\tau = 0.50$), input size ($3 \times 224 \times 224$), and Dataset A held-out test partition ($N = 138$) remain untouched.
- **Dataset B Governance**: External dataset B remains strictly quarantined under `PERMISSION_REQUIRED` without unauthorized image acquisition.
- **Existing Backend Endpoints**: Retained all existing routes across `/api/health`, `/api/auth`, `/api/animals`, `/api/detection`, `/api/epidemiology`, `/api/evaluation`, `/api/alerts`, and `/api/veterinary`. Legacy case review and single-medicine treatment payloads continue to function seamlessly.
- **Frontend Core Structure**: Preserved existing React 18 / Vite / Tailwind structure and routes (`/`, `/animals`, `/disease-detection`, `/reports`, `/veterinary`, `/alerts`, `/analytics`).

---

### 3. Veterinary Workflow Lifecycle
The workflow enforces a strict 5-stage finite state machine:

```
[ Farmer / AI Screening Detection ]
                ↓
         PENDING_REVIEW  (Initial triage, awaiting physical auscultation/inspection)
                ↓  (Veterinary clinical examination & decision)
            REVIEWED     (Vet decision recorded: Accepted / Modified / Urgent)
                ↓  (Prescription of approved pharmaceutical & supportive care)
        TREATMENT_ACTIVE (Medications active, quarantine/isolation enforced)
                ↓  (Scheduling physical clinical re-examination)
           FOLLOW_UP     (Target checkup date & post-treatment monitoring)
                ↓  (Lesions resolved, full recovery confirmed)
             CLOSED      (Case archived with complete audit trail)
```

**Lifecycle Transition Rules & Safeguards**:
- Direct transition from `PENDING_REVIEW` to `TREATMENT_ACTIVE` is strictly prohibited (returns HTTP 400 Bad Request).
- Direct closure of a case while still in `PENDING_REVIEW` is prohibited (returns HTTP 400 Bad Request).
- Modification or clinical review of a `CLOSED` case is prohibited without administrative audit (returns HTTP 400 Bad Request).

---

### 4. Database Schema & Changes
All cases are stored in MongoDB collection `anicare_ai.veterinary_cases`. The extended case document structure includes:
```json
{
  "case_id": "CASE-2026-XXXX",
  "animal_id": "AN-GJ-2024-XXXX",
  "animal_tag": "TAG-XXXX",
  "animal_name": "Ganga Crossbreed",
  "species": "Cattle (Bos indicus)",
  "owner_name": "Rameshbhai Patel",
  "location": "North Shed 03",
  "risk_level": "HIGH",
  "case_status": "PENDING_REVIEW | REVIEWED | TREATMENT_ACTIVE | FOLLOW_UP | CLOSED",
  "ai_assessment": {
    "possible_condition": "Suspected Lumpy Skin Disease",
    "confidence": 88.5,
    "risk_level": "HIGH",
    "explanation": "Circumscribed cutaneous nodular eruptions detected.",
    "symptoms_detected": ["Cutaneous nodules", "Pyrexia 104.2 F"],
    "recommended_immediate_actions": ["Insect-proof quarantine", "Palpate nodules"],
    "veterinary_review_required": true
  },
  "vet_review": {
    "status": "REVIEWED",
    "vet_id": "USR-VET-001",
    "vet_name": "Dr. Rajesh Patel",
    "vet_license_no": "VET-REG-88402-GJ",
    "decision": "AI_ASSESSMENT_ACCEPTED",
    "clinical_notes": "Clinical physical examination confirms acute nodular eruptions.",
    "veterinary_assessment": "Confirmed Acute Lumpy Skin Disease",
    "reviewed_at": "2026-10-08T13:46:01Z"
  },
  "treatment_plan": {
    "diagnosis_assessment": "Acute Lumpy Skin Disease",
    "medicines": [
      {
        "medicine_name": "Meloxicam 5mg/ml",
        "dosage": "0.5 mg/kg SC once daily",
        "frequency": "Once daily",
        "duration": "3 days",
        "route": "Subcutaneous (SC)",
        "instructions": "Administer with sterile needle under antiseptic skin preparation."
      }
    ],
    "supportive_care": "Antiseptic povidone-iodine wash on ruptured papules.",
    "isolation_required": true,
    "prescribed_by": "Dr. Rajesh Patel",
    "prescription_license": "VET-REG-88402-GJ",
    "treatment_start_date": "2026-10-08"
  },
  "follow_up": {
    "required": true,
    "follow_up_date": "2026-10-14",
    "notes": "Assess nodule scab detachment and temperature return to baseline.",
    "completed": false
  },
  "audit_trail": [
    {
      "action": "CASE_CREATED",
      "user_id": "USR-SYSTEM-AI",
      "user_role": "system",
      "details": "Auto-escalated HIGH risk screening.",
      "timestamp": "2026-10-08T13:46:01Z"
    }
  ],
  "created_at": "2026-10-08T13:46:01Z",
  "updated_at": "2026-10-08T13:46:01Z"
}
```

---

### 5. API Endpoints (Added & Extended)

| HTTP Method | Route | Description | RBAC & Validation |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/veterinary/stats` | Real-time aggregate metrics from MongoDB (`pending_reviews`, `high_critical_cases`, `active_treatments`, `follow_ups_due`, `closed_cases`, `total_cases`). | Public / Authenticated |
| `GET` | `/api/veterinary/cases` | Filter cases by `status`, `risk`, `animal_id`, with pagination. | Public / Authenticated |
| `POST` | `/api/veterinary/cases` | Escalates or creates a new veterinary clinical case in `PENDING_REVIEW`. | Authenticated / System |
| `GET` | `/api/veterinary/cases/{case_id}` | Retrieves full case dossier with AI screening history, review notes, treatments, and audit trail. | Authenticated |
| `PUT` | `/api/veterinary/cases/{case_id}/review` | Records vet clinical decision (`AI_ASSESSMENT_ACCEPTED`, `AI_ASSESSMENT_MODIFIED`, etc.), notes, and transitions status to `REVIEWED`. | Vet Only (Farmers blocked 403) |
| `POST` | `/api/veterinary/cases/{case_id}/treatment` | Prescribes approved pharmaceutical regimen and supportive care; transitions status to `TREATMENT_ACTIVE`. | Vet Only + Certified License Required (Farmers & Admins blocked 403) |
| `POST` / `PUT` | `/api/veterinary/cases/{case_id}/follow-up` | Schedules clinical follow-up examination date and monitoring objectives; transitions status to `FOLLOW_UP`. | Vet Only (Farmers blocked 403) |
| `PUT` | `/api/veterinary/cases/{case_id}/close` | Formally closes case following recovery; transitions status to `CLOSED`. | Vet Only (Blocked if still pending review) |

---

### 6. Role-Based Security (RBAC)
Endpoint access is strictly partitioned according to veterinary medical ethics and statutory requirements:
1. **Farmer Role**:
   - Authorized to view animal status, active treatment regimens, supportive instructions, and scheduled follow-up dates.
   - Strictly forbidden (HTTP 403) from approving AI assessments, modifying clinical findings, creating medical prescriptions, scheduling clinical follow-ups, or closing cases.
2. **Veterinarian Role**:
   - Authorized to perform full clinical triage, accept or modify AI hypotheses, enter clinical physical observations, prescribe antimicrobials and supportive drugs under valid license registration, schedule follow-ups, and discharge patients.
3. **Administrator Role**:
   - Authorized to monitor system telemetry, track epidemiological metrics, and review caseloads.
   - Strictly forbidden (HTTP 403) from prescribing pharmaceutical medications without certified veterinary credentials.

---

### 7. Clinical Safety Controls & Disclaimers
1. **Probabilistic Screening Guard**: AI model outputs are universally phrased across UI and API as:
   - *"AI Suggested Condition"*
   - *"AI Risk Assessment"*
   - *"Veterinary Decision & Confirmed Assessment"*
2. **Statutory AI Warning Banner**: Displayed prominently in all case views:
   > *"VETERINARY MEDICAL DISCLAIMER: Artificial Intelligence outputs represent probabilistic screening hypotheses to assist clinical triage. Final clinical diagnosis and pharmaceutical intervention must be established solely by a certified Veterinary Medical Officer."*
3. **Statutory License Enforcement**: Prescribing veterinarians must provide a valid Veterinary Council registration number ($\ge 5$ characters). Submissions with missing, whitespace, or abbreviated licenses are rejected with HTTP 400 Bad Request.

---

### 8. Regulatory Audit Trail
Every clinical action appends an immutable entry to the case's `audit_trail` array:
- `CASE_CREATED`: Auto-escalated from AI triage or created manually.
- `CASE_REVIEWED`: Clinical decision recorded by attending veterinarian.
- `TREATMENT_CREATED`: Approved medication regimen and supportive care prescribed.
- `FOLLOW_UP_SCHEDULED`: Post-treatment checkup date and objectives registered.
- `CASE_CLOSED`: Final resolution and discharge confirmed.

---

### 9. Frontend UI Enhancements
Upgraded `src/pages/VeterinaryCare.jsx`:
- **Real-Time Dynamic Metrics Banner**: 6 KPI cards displaying live MongoDB aggregate counts for Pending Reviews, High/Critical Risk, Active Treatments, Follow-ups Due, Closed Cases, and Total Pipeline.
- **Filter Navigation**: Interactive pill buttons filtering by status (`All`, `Pending Review`, `Reviewed`, `Treatment Active`, `Follow-Up Due`, `Closed`) and risk level dropdown (`Critical`, `High`, `Moderate`, `Low`).
- **Comprehensive 4-Stage Decision Support Modal**:
  - *Stage 1: AI Screening & Triage Overview*: Full patient demographics, condition suggestion, confidence bar, risk badges, recommended checklist, and safety warning.
  - *Stage 2: Veterinary Review Form*: Decision dropdown, confirmed assessment input, attending vet name, council license number, and clinical observations.
  - *Stage 3: Pharmaceutical & Supportive Regimen Form*: Dynamic multi-medicine rows (name, dosage, frequency, duration, route), supportive care instructions, isolation toggle, and prescribing license guard.
  - *Stage 4: Follow-up & Case Closure Form*: Date picker for scheduled checkups, follow-up objectives, recovery resolution summary, and formal discharge.
  - *Stage 5: Chronological Regulatory Audit Trail*: Visual timeline tracking all operators, timestamps, actions, and details.

---

### 10. Automated Test Suite
Implemented dedicated test suite [`backend/tests/test_milestone9a_veterinary_workflow.py`](file:///d:/AniCare-AI/backend/tests/test_milestone9a_veterinary_workflow.py) with 8 targeted tests:
1. `test_veterinary_stats_endpoint`: Verifies `/api/veterinary/stats` returns valid aggregate integers from MongoDB.
2. `test_veterinary_case_creation_and_initial_state`: Verifies initial status `PENDING_REVIEW` and initial audit log.
3. `test_full_decision_support_workflow_lifecycle`: Validates complete lifecycle (`PENDING_REVIEW` $\to$ `REVIEWED` $\to$ `TREATMENT_ACTIVE` $\to$ `FOLLOW_UP` $\to$ `CLOSED`).
4. `test_invalid_status_transitions_rejected`: Verifies state-machine enforcement (rejecting premature treatment, premature close, and editing closed cases).
5. `test_role_based_security_authorization`: Verifies farmers and admins are blocked (HTTP 403) and vets authorized.
6. `test_statutory_license_validation_edge_cases`: Verifies empty and invalid license strings are rejected (HTTP 400).
7. `test_ai_screening_escalation_to_pending_veterinary_case`: Verifies critical screening automatically generates a case in `PENDING_REVIEW`.
8. `test_case_filtering_by_status_and_risk`: Verifies query filtering by status and risk level.

---

### 11. Verification Results
- **Full Backend Pytest Suite**: **122 passed out of 122 tests** in 14.88 seconds with 0 failures and 0 errors.
- **Milestone 9A Test Suite**: **8 passed out of 8 tests** with 100% pass rate.
- **Frontend Production Build**: `npm run build` completed successfully with **0 errors** (1,940 modules transformed, assets bundled in 17.97s).
- **Backend API Health Check**: `GET /api/health` returns `200 OK`, `status: "healthy"`, database `anicare_ai` connected (1.41ms latency).
- **Live Cases Verification**: `GET /api/veterinary/cases` verified with active MongoDB persistence and audit trail logging.

---

### 12. Limitations & Next Milestone
- **Current Limitation**: Tele-consultation video rooms remain simulated web hooks for demonstration purposes.
- **Antimicrobial Resistance (AMR) Tracking**: Formal drug-class resistance counters and withdrawal period alerts will be expanded in Milestone 9B.
- **Next Milestone**: Milestone 9B will focus on epidemiological heatmaps, district-level outbreak escalation alerts, and automated farmer SMS/WhatsApp advisory feeds.
