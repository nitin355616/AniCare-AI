# AniCare AI — Milestone 9C Technical Report
## Outbreak Intelligence & Syndromic Early Warning System

---

### 1. Objective
The primary objective of Milestone 9C is to transform the **AniCare AI — AI-Powered Animal Health & Disease Early Warning System** (SIH 2026) from an individual-animal clinical decision support platform into a **herd, village, block, district, state, and national-level syndromic surveillance command center**.

The intelligence pipeline bridges animal-level visual screening and IoT telemetry with certified Veterinary Medical Officer response and state governmental early warnings:
```
Animal Health Event / Visual Screening
                ↓
Animal Risk Score & Telemetry Signals
                ↓
Disease / Condition Signal Extraction
                ↓
Spatial & Sliding Temporal Window Aggregation (7D / 14D / 30D)
                ↓
Administrative Jurisdictional Analysis (Village → Block → District → State)
                ↓
Spatial-Temporal Cluster Detection
                ↓
Explainable Outbreak Risk Scoring (0–100)
                ↓
Outbreak Risk Tier Resolution (Tier 1 Routine, Tier 2 Surveillance, Tier 3 Red Alert)
                ↓
Automatic Early Warning Alert Dispatch (with Deduplication)
                ↓
Veterinary Officer Assignment
                ↓
Certified On-Site Clinical Field Investigation
                ↓
Government / DAHD Command Center Dashboard
                ↓
Precautionary Containment, Ring Vaccination & Monitoring
                ↓
Cluster Resolution / False Alert Discharge
```

**Non-Negotiable Safety Principle**:
> *AniCare AI provides early-warning decision support and does not independently confirm disease outbreaks.*  
No cluster detection or syndromic alert is ever treated as a legally confirmed disease outbreak without regulatory laboratory diagnostic confirmation (e.g., RT-PCR, ELISA, viral isolation) and formal notification by the State Department of Animal Husbandry (DAHD).

---

### 2. Architecture & Foundation Preservation
Milestone 9C was engineered on top of existing components with 100% backward compatibility and zero regression:
- **Vision Model Weights & Configuration**: The production EfficientNet-B0 ONNX model (`anicare_vision_bovine_v1.onnx`), frozen operating threshold ($\tau = 0.50$), input size ($3 \times 224 \times 224$), and Dataset A held-out test partition ($N = 138$) remain untouched.
- **Dataset B Governance**: External dataset B remains strictly quarantined under `PERMISSION_REQUIRED` without unauthorized image acquisition.
- **Clinical Lifecycle Governance**: All Milestones 9A and 9B workflows (5-stage case lifecycle, multi-medicine formulations, biosecurity prevention planning, food safety milk/meat withdrawal tracking, vaccination logging) continue to function with zero interference.
- **Existing Backend Endpoints**: Retained all existing routes across `/api/health`, `/api/auth`, `/api/animals`, `/api/detection`, `/api/epidemiology`, `/api/evaluation`, `/api/alerts`, and `/api/veterinary`.
- **Frontend Core Structure**: Preserved existing React 18 / Vite / Tailwind structure and routes (`/`, `/animals`, `/disease-detection`, `/reports`, `/veterinary`, `/alerts`, `/analytics`), extending with the dedicated `/outbreaks` route.

---

### 3. Cluster Detection Logic
The cluster detection engine aggregates animal health events from `veterinary_cases`, `disease_assessments`, and `animals` without creating a redundant secondary machine learning model.

#### Decision-Support Constants:
```python
CLUSTER_MIN_CASES = 3      # Minimum at-risk cases in jurisdiction to trigger cluster
HIGH_RISK_MIN_CASES = 3    # Minimum high/critical cases
RED_ALERT_MIN_CASES = 5    # Minimum caseload volume for Red Alert escalation
DEFAULT_WINDOW_DAYS = 7    # Default sliding temporal window
```

#### Detection Rules:
1. **Baseline Spatial Cluster (`POSSIBLE_CLUSTER`)**:
   $$\ge 3\text{ high/critical-risk animals} \land \text{same village/block} \land \text{same disease signal} \land \text{within sliding window (7 days)}$$
   $\longrightarrow$ Assigns **`TIER_2_SURVEILLANCE`**. Priority veterinary on-site verification recommended within 24 hours.

2. **Severe Outbreak Signal (`SUSPECTED_OUTBREAK`)**:
   $$\ge 5\text{ high/critical-risk animals} \land \text{same geographic area} \land \text{within sliding window} \land \text{increasing case trajectory}$$
   $\longrightarrow$ Assigns **`TIER_3_RED_ALERT`**. Immediate emergency dispatch of District Veterinary Officer (DVO) containment unit and 5km ring vaccination advisory.

3. **Geographic Hierarchy**:
   Aggregates across `State` $\to$ `District` $\to$ `Block` $\to$ `Village`.
   If location data is unavailable, the system strictly assigns `LOCATION_UNKNOWN` without fabricating fictitious GPS coordinates.

---

### 4. Explainable Outbreak Risk Scoring
Rather than relying on an opaque deep learning model, the Outbreak Risk Score ($0–100$) is strictly explainable and deconstructible into 5 clinical and spatial components:

| Scoring Component | Point Contribution | Rationale / Trigger Rule |
| :--- | :---: | :--- |
| **Caseload Volume** | Up to 35 pts | $\ge 8$ cases: +35 pts; $\ge 5$ cases: +25 pts; $\ge 3$ cases: +15 pts; $<3$ cases: +5 pts |
| **Clinical Severity** | Up to 35 pts | Critical cases: +10 pts each (max 20); High-risk cases: +5 pts each (max 15) |
| **Temporal Growth** | Up to 15 pts | Growth $\ge +100\%$: +15 pts; Growth $> 0\%$: +10 pts; Flat trend: +5 pts |
| **Geographic Density** | Up to 10 pts | Concentrated in specific village: +10 pts; In district: +5 pts |
| **Pathogen Homogeneity** | Up to 5 pts | 100% concordance on condition signal: +5 pts |

Each event dossier includes explicit, user-facing `trigger_reasons` articulating exactly why points were added.

---

### 5. Outbreak Risk Tiers & Terminology
AniCare AI enforces rigorous, non-alarmist scientific terminology:

- **`TIER_1_ROUTINE`** (Score $< 40$, $< 3$ cases):
  Normal epidemiological baseline. Standard dairy hygiene and routine syndromic surveillance recommended.
- **`TIER_2_SURVEILLANCE`** (Score $40–74$ or $\ge 3$ clustered cases):
  Early signal detected (`POSSIBLE_CLUSTER`). On-site veterinary clinical verification required within 24 hours; isolate cohort cattle under insect mesh.
- **`TIER_3_RED_ALERT`** (Score $\ge 75$ or $\ge 5$ cases with critical severity/surge):
  High-probability transmission surge (`SUSPECTED_OUTBREAK`). Emergency District Veterinary Officer dispatch, 100m standoff quarantine, vehicle transit suspension, and 5km ring vaccination advisory.

---

### 6. Outbreak Status Workflow
Every outbreak event traverses a certified lifecycle state machine:
```
DETECTED
   ↓
UNDER_SURVEILLANCE
   ↓ (Officer Assigned)
VETERINARY_INVESTIGATION
   ↓ (Field Inspection Recorded)
ACTION_RECOMMENDED
   ↓ (Precautionary Containment Enacted)
MONITORING
   ↓ (14 Days Without New Cases)
RESOLVED
```
Alternatively, if clinical scraping and inspection confirm non-infectious etiology (e.g. non-contagious insect bites or localized allergy), the event can be transitioned to:
```
FALSE_ALERT
```
This unburdens field response units while preserving the audit record.

---

### 7. Database Schemas & Collections
Milestone 9C introduces the dedicated `outbreak_events` collection in MongoDB (`anicare_ai`):

#### Indexed Fields:
- `event_id`: Unique identifier (`OUT-2026-XXXX`).
- `status`: Lifecycle status (`DETECTED`, `UNDER_SURVEILLANCE`, `VETERINARY_INVESTIGATION`, `ACTION_RECOMMENDED`, `MONITORING`, `RESOLVED`, `FALSE_ALERT`).
- `risk_tier`: `TIER_1_ROUTINE`, `TIER_2_SURVEILLANCE`, `TIER_3_RED_ALERT`.
- `district`, `village`, `disease_signal`, `is_demo`.
- Compound timestamp indices: `[("created_at", -1)]`, `[("last_updated_at", -1)]`.

#### Pydantic Data Contract:
- `LocationHierarchy`: `village`, `block`, `district`, `state`, `pincode`.
- `InvestigationRecord`: `field_visit_date`, `animals_examined`, `clinical_observations`, `suspected_condition`, `laboratory_test_required`, `laboratory_test_status`, `preventive_actions`, `biosecurity_actions`, `farmer_guidance`, `follow_up_date`, `investigating_officer`, `officer_license`.
- `OutbreakAuditEvent`: `action`, `actor_id`, `actor_role`, `timestamp`, `event_id`, `previous_status`, `new_status`, `notes`.
- `OutbreakEventResponse`: Complete dossier with location, score, triggers, recommendations, audit history, and statutory disclaimer.

---

### 8. API Endpoints
The following REST endpoints are registered under `/api/outbreaks`:

| Endpoint | Method | Role Authorization | Purpose |
| :--- | :---: | :---: | :--- |
| `/api/outbreaks` | `GET` | All (Farmer/Vet/Admin) | Query active cluster events with status, tier, and district filters |
| `/api/outbreaks/{event_id}` | `GET` | All | Fetch comprehensive event dossier including animal details and audit trail |
| `/api/outbreaks/stats` | `GET` | All | Real-time surveillance KPIs (active clusters, red alerts, affected counts) |
| `/api/outbreaks/trends` | `GET` | All | 7-day, 14-day, and 30-day temporal trend analytics and percentage growth |
| `/api/outbreaks/hotspots` | `GET` | All | Administrative hierarchy caseload aggregation (`HOTSPOT_HIGH`, `MEDIUM`, `LOW`) |
| `/api/outbreaks/scan` | `POST` | **Vet & Admin (403 for Farmer)** | Triggers automated syndromic scanning sweep across livestock cases |
| `/api/outbreaks/seed-demo` | `POST` | **Vet & Admin (403 for Farmer)** | Seeds synthetic SIH 2026 demonstration cluster in Village Demo-A |
| `/api/outbreaks/{event_id}/assign` | `POST` | **Vet & Admin (403 for Farmer)** | Assigns Veterinary Medical Officer and updates status |
| `/api/outbreaks/{event_id}/status` | `PUT` | **Vet & Admin (403 for Farmer)** | Transitions operational status (e.g. `MONITORING`, `RESOLVED`, `FALSE_ALERT`) |
| `/api/outbreaks/{event_id}/investigation`| `POST` | **Vet & Admin (403 for Farmer)** | Submits certified clinical field inspection and lab assay orders |

---

### 9. Real-Time Alert Integration & Deduplication
When a cluster crosses into `TIER_2_SURVEILLANCE` or `TIER_3_RED_ALERT`:
1. The service dispatches an alert into `anicare_ai.alerts` with category `critical` (for Red Alert) or `disease-risk` (for Surveillance).
2. **Deduplication Safeguard**: The system queries active alerts for the same event ID (`affected_tag matching event_id`) and updates existing alerts rather than generating spam.
3. When an event is marked `RESOLVED` or `FALSE_ALERT`, all associated active alerts are automatically marked as `Resolved`.

---

### 10. Role-Based Access Control (RBAC)

| Operational Capability | Farmer | Veterinarian | Administrator |
| :--- | :---: | :---: | :---: |
| View Surveillance Dashboard & Hotspots | Allowed | Allowed | Allowed |
| View Outbreak Dossiers & Trends | Allowed | Allowed | Allowed |
| Trigger Syndromic Sliding Scans | **Blocked (403)** | Allowed | Allowed |
| Seed SIH Demo Clusters | **Blocked (403)** | Allowed | Allowed |
| Assign Veterinary Officers | **Blocked (403)** | Allowed | Allowed |
| Submit Certified Field Investigations | **Blocked (403)** | Allowed | Allowed |
| Change Outbreak Status (Resolve / False Alert)| **Blocked (403)** | Allowed | Allowed |

---

### 11. Immutable Audit Trail
Every lifecycle state change and clinical intervention is captured in the event's `audit_trail` array:
- `CLUSTER_DETECTED`: Initial spatial grouping trigger.
- `CLUSTER_TELEMETRY_UPDATED`: Metrics updated during subsequent scan.
- `OFFICER_ASSIGNED`: Assignment of Veterinary Medical Officer.
- `INVESTIGATION_RECORDED`: Submission of field inspection record.
- `STATUS_CHANGED`: Transitions between lifecycle stages.
- `DEMO_CLUSTER_SEEDED`: Synthetic presentation cluster initialized.

---

### 12. Controlled SIH 2026 Demonstration Mode
For jury presentations, the platform includes a controlled demo workflow accessible via `POST /api/outbreaks/seed-demo` and the UI "Seed SIH Demo Outbreak" button:
- **Jurisdiction**: `Village Demo-A`, `Anand Rural`, `Anand District`, `Gujarat` (Pincode: `388001`).
- **Caseload**: 5 cattle cases (`AN-DEMO-01` to `AN-DEMO-05`).
- **Condition**: Suspected Lumpy Skin Disease (Capripoxvirus Cluster).
- **Risk Score**: 95 / 100 (`TIER_3_RED_ALERT`).
- **Tagging**: Explicitly flagged with `is_demo: true`, displaying prominent `DEMO DATA` badges. Real production livestock records remain isolated.

---

### 13. Frontend Outbreak Command Center
- **Route**: [`/outbreaks`](file:///d:/AniCare-AI/src/pages/OutbreakIntelligence.jsx)
- **Navigation**: Registered in [`src/App.jsx`](file:///d:/AniCare-AI/src/App.jsx) and linked via [`src/components/layout/Sidebar.jsx`](file:///d:/AniCare-AI/src/components/layout/Sidebar.jsx) with Radio icon and "Early Warn" badge.
- **UI Architecture**:
  1. **Surveillance Header**: Live status banner, "Scan For Clusters Now" button, "Seed SIH Demo Outbreak" CTA.
  2. **KPI Banner**: Active Clusters, Red Alerts, Surveillance Alerts, Affected Animals, Affected Villages, Affected Districts.
  3. **3 Interactive Command Views**:
     - *Active Cluster Events*: Filterable table with Risk Gauge, Caseload, Risk Tier, Status, Assigned Officer, and Open Dossier action.
     - *Geographic Hotspots*: Administrative hierarchy view (`HOTSPOT_HIGH`, `MEDIUM`, `LOW`).
     - *Satellite & Radar Basin*: Embedded drone & satellite geo-telemetry visualizer.
  4. **Temporal Trajectory Bar**: Toggle between 7D, 14D, and 30D sliding windows with growth percentage.
  5. **Comprehensive Outbreak Dossier Modal**:
     - Sub-Tab 1: Explainable Risk Score & Trigger Reasons.
     - Sub-Tab 2: Affected Livestock Roster.
     - Sub-Tab 3: Visual Early Warning Escalation Timeline (Day 1 $\to$ Day 3 $\to$ Day 5 $\to$ Day 7).
     - Sub-Tab 4: Field Investigation & Officer Assignment Form.
     - Sub-Tab 5: Immutable Chronological Audit Trail.

---

### 14. Verification & Automated Test Results
- **Milestone 9C Test Suite**: [`backend/tests/test_milestone9c_outbreak_intelligence.py`](file:///d:/AniCare-AI/backend/tests/test_milestone9c_outbreak_intelligence.py)
  - 8 / 8 tests passing:
    1. `test_cluster_detection_logic_and_scoring_unit`: Location parsing and explainable scoring unit logic.
    2. `test_outbreak_scan_and_cluster_generation`: Scanning cases in same village creates cluster event.
    3. `test_alert_generation_and_deduplication`: Alert triggered and deduplication verified.
    4. `test_rbac_farmer_blocked_vet_admin_permitted`: Farmers blocked with 403 on scan, seed, assign, status, and investigation.
    5. `test_veterinary_officer_assignment_workflow`: Assignment updates officer name, status, and audit log.
    6. `test_clinical_field_investigation_and_status_transitions`: Submits investigation and transitions to MONITORING and RESOLVED.
    7. `test_false_alert_workflow`: Marks event as FALSE_ALERT with audit log.
    8. `test_trends_hotspots_and_sih_demo_cluster`: Verifies stats, trends, hotspots, and demo cluster seeding.
- **Full Backend Test Suite**: **138 / 138 tests passing** (`pytest` in 14.26s, 0 errors).
- **Frontend Production Build**: `npm run build` completed cleanly in 13.37s (0 errors, 1,943 modules).
- **Live API Health**: `http://127.0.0.1:8000/api/health` returned HTTP 200 OK (latency: `1.35 ms`).
- **Live Outbreak Stats**: `http://127.0.0.1:8000/api/outbreaks/stats` returned HTTP 200 OK.

---

### 15. Known Limitations & Future Improvements
1. **Administrative Boundary Disambiguation**: In villages with identical names across adjacent blocks, manual block specification is encouraged to ensure exact clustering.
2. **Confirmatory Lab Integration**: In the current MVP, laboratory assay status (`SAMPLES_SENT`, `AWAITING_RESULTS`, `CONFIRMED_POSITIVE`) is recorded manually by Veterinary Officers. Future milestones will interface directly with ICAR-DFMD / State LIMS portals.
3. **Multi-Species Syndromic Cross-Correlation**: Currently specialized for bovine cutaneous and vesicular conditions. Caprine and avian syndrome tracking will be activated in Milestone 9D.
