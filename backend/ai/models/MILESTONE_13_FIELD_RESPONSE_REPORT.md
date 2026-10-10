# AniCare AI — Milestone 13: Field Response, Alert Orchestration & Government Action Workflow Report

**Project:** AniCare AI (SIH 2026 National Hackathon)  
**Milestone:** 13 — Operational Field Response, Alert Orchestration & Government Action Workflow  
**Status:** COMPLETE & AUDITED  
**Date:** 2026-10-08  
**Model Weights Status:** FROZEN (`anicare_vision_bovine_v1.onnx`, 15.29 MB, opset 14, $\tau = 0.50$, SHA-256 `594d42c7d12fd32a4d22dc7f4cd32156162cb6170e05a432b2010d306f5f4f8d`)  
**External Dataset B Status:** QUARANTINED (`PERMISSION_REQUIRED`)  
**Backend Automated Test Suite:** **222 / 222 PASS (100% Pass Rate)**  
**Frontend Production Build:** **PASS (0 Errors, 1,984 modules transformed)**  

---

## 1. Executive Summary & Objective

Milestone 13 transforms AniCare AI from an early-warning signal detection system into an **operational, auditable, and human-authorized veterinary field response platform**. 

While Milestones 1–12 established lesion screening, syndromic surveillance, offline synchronization, continuous model drift monitoring, and coarse geospatial risk mapping, Milestone 13 implements the **operational response layer**:

$$\text{Risk Detection} \to \text{Alert Generation} \to \text{Assignment} \to \text{Field Investigation} \to \text{Specimen Collection} \to \text{Lab Diagnostics} \to \text{Department Review} \to \text{Authorized Action} \to \text{Resolution}$$

### Statutory Decision-Support Principle
> **“AI-generated risk signals support prioritization. Field investigation and authorized veterinary/department decisions remain human-controlled.”**

AniCare AI explicitly forbids:
- Autonomous government decision-making
- Autonomous clinical diagnosis
- Autonomous prescription dispensation
- Autonomous vaccination orders
- Autonomous outbreak confirmations

---

## 2. System Architecture

```text
                                  AniCare AI
                                       │
                    ┌──────────────────┼──────────────────┐
                    │                  │                  │
                AI Vision        Farmer Portal        Veterinary
                    │                  │                  │
                    └──────────────────┼──────────────────┘
                                       ↓
                                Multimodal Risk
                                       ↓
                            Outbreak Intelligence
                                       ↓
                           Geospatial Intelligence
                                       ↓
                                 Risk Hotspot
                                       ↓
                              RESPONSE ENGINE
                                       │
             ┌─────────────────────────┼─────────────────────────┐
             ↓                         ↓                         ↓
           ALERT                 INVESTIGATION               ASSIGNMENT
             │                         │                         │
             └─────────────────────────┼─────────────────────────┘
                                       ↓
                                 FIELD EVIDENCE
                                       ↓
                                  SAMPLE / LAB
                                       ↓
                              DEPARTMENT REVIEW
                                       ↓
                             AUTHORIZED ACTION
                                       ↓
                                 FOLLOW-UP
                                       ↓
                                 RESOLUTION
                                       ↓
                             RISK RECALCULATION
                                       ↓
                               AI MONITORING
                                       ↓
                            GOVERNED IMPROVEMENT
```

---

## 3. Workflow State Machine

The response engine implements an auditable 14-state operational lifecycle:

1. `RISK_DETECTED`: Geospatial hotspot, outbreak event, or critical syndromic pattern detected.
2. `ALERT_GENERATED`: Operational response alert generated with automatic deduplication.
3. `ALERT_ACKNOWLEDGED`: Recognized by designated veterinary authority (e.g. DVO).
4. `INVESTIGATION_ASSIGNED`: Field Veterinary Officer assigned with SLA completion deadline.
5. `FIELD_INVESTIGATION`: On-site visit conducted; animals observed, clinical symptoms, and biosecurity recorded.
6. `VETERINARY_ASSESSMENT`: Clinical triage evaluating containment necessity.
7. `SAMPLE_COLLECTION`: Biological specimens collected under cold-chain standards.
8. `LAB_PENDING`: Specimen accessioned at state diagnostic laboratory.
9. `LAB_RESULT_RECORDED`: Confirmatory assay results recorded (`POSITIVE`, `NEGATIVE`, `INCONCLUSIVE`).
10. `DEPARTMENT_REVIEW`: Mandatory human administrative review by Joint Director / State DAHD.
11. `ACTION_AUTHORIZED`: Government sanction for ring vector control, livestock movement restrictions, or targeted sampling.
12. `ACTION_IN_PROGRESS`: Containment protocols enacted on the ground.
13. `FOLLOW_UP`: Veterinary re-inspection evaluating clinical regression and secondary spread.
14. `RESOLVED`: Official case closure with post-closure geospatial risk recalculation.

---

## 4. Operational Alert Engine, Deduplication & Escalation

### Priority Mapping
- **P1 — CRITICAL** ($\text{Risk Score} \ge 80.0$): Urgent operational field investigation priority. *Does not equate to a confirmed outbreak.*
- **P2 — HIGH** ($60.0 \le \text{Risk Score} < 80.0$): High-priority surveillance alert.
- **P3 — MODERATE** ($30.0 \le \text{Risk Score} < 60.0$): Routine monitoring alert.
- **P4 — MONITORING** ($\text{Risk Score} < 30.0$): Passive surveillance.

### Alert Deduplication
To prevent alert fatigue and redundant notifications across recalculation cycles:
$$\text{Key} = \text{source\_id} + \text{alert\_type} + \text{status} \in \{\text{ACTIVE}, \text{ALERT\_GENERATED}, \text{ACKNOWLEDGED}\}$$
When an active alert matches the key, the existing record is updated with fresh risk telemetry rather than duplicating records.

### Auditable Escalation
Alerts escalate (e.g., $P3 \to P2 \to P1$) upon emerging epidemiological evidence (rising case burden, widening herd involvement). Every escalation logs:
```json
{
  "from_priority": "P3",
  "to_priority": "P1",
  "reason": "Rapid spike in affected herds reported by cooperative",
  "timestamp": "2026-10-08T17:42:00Z",
  "actor": "District Veterinary Officer"
}
```

---

## 5. Role-Based Access Control (RBAC) & Permission Scopes

| Role | Permitted Actions | Prohibited Operations (HTTP 403 Forbidden) |
| :--- | :--- | :--- |
| **Farmer** | View own alerts, request doctor visits, view own animal recovery | Cannot view government hotspot maps, assign officers, escalate alerts, view other farmers' data, or authorize department actions |
| **Veterinarian** | View assigned cases, acknowledge alerts, record clinical findings, collect samples, schedule follow-ups | Cannot authorize department-level statutory containment without explicit administrative role |
| **Field Officer** | View assigned visits, record physical herd observations, upload evidence, package laboratory samples | Cannot alter original AI model predictions or authorize quarantine rings |
| **Lab User** | Access pending specimens, record assay results (`POSITIVE`, `NEGATIVE`, `INCONCLUSIVE`, `INVALID`) | Cannot alter AI vision scores or autonomously order field quarantine |
| **Department Officer / Admin** | Assign officers, review lab evidence, authorize statutory containment/biosecurity actions, close cases | Cannot bypass immutable audit log or alter original AI vision weights |

---

## 6. Field Investigation & Evidence Security

### On-Site Inspection Schema
Each field visit captures:
- Animals examined count
- Affected animals count
- Herds inspected count
- Clinical symptoms observed (standardized veterinary ontology)
- Enclosure & biosecurity conditions (vector exposure, drainage, perimeter)
- Mortality count (if any)
- Investigating officer identity and timestamp

### Evidence File Upload Guard
1. **Extension Allowlist**: Strictly `.jpg`, `.jpeg`, `.png`, `.pdf`.
2. **Executable Rejection**: `.exe`, `.bat`, `.js`, `.sh`, `.zip`, `.py`, `.vbs`, `.msi` rejected with `HTTP 400 Bad Request`.
3. **Payload Limit**: Maximum 10 MB per file.
4. **Integrity Hashing**: Cryptographic SHA-256 hash calculated upon upload for evidence tamper-evidence.

---

## 7. Biological Specimen Tracking & Non-Autonomous Lab Assays

### Cold-Chain Specimen Lifecycle
Specimens (`SWAB`, `BLOOD`, `SERUM`, `SCAB_TISSUE`, `MILK`) transition through:
$$\text{COLLECTED} \to \text{TRANSPORTED} \to \text{LAB\_PENDING} \to \text{PROCESSING} \to \text{RESULT\_AVAILABLE}$$

### Clinical Safety Non-Autonomous Invariant
A positive laboratory diagnostic assay (e.g., *Capripoxvirus RT-PCR POSITIVE, Ct = 21.4*) **NEVER autonomously triggers medication or containment**. It automatically advances the case to `DEPARTMENT_REVIEW`, ensuring that human veterinary epidemiologists determine containment perimeters, ring boundaries, and legal notifications.

---

## 8. Department Authorization & Case Closure Safeguards

### Authorized Intervention Types
1. `BIOSECURITY_REVIEW`: Ring vector control, insect repellent spraying, herd isolation.
2. `AUTHORIZED_CONTAINMENT`: Movement restrictions on livestock in infected zones.
3. `FIELD_RECHECK`: Secondary verification visit scheduled within 48 hours.
4. `AUTHORIZED_VACCINATION_REVIEW`: Emergency ring vaccination strategy audit.
5. `ADDITIONAL_SAMPLING`: Expanded serological surveillance.
6. `FARMER_GUIDANCE`: Bilingual advisory distribution.

### Critical Case Closure Guard
A `P1 CRITICAL` response case **cannot be closed prematurely**. The API strictly verifies that on-site field investigation records exist before permitting `RESOLVED` closure.

---

## 9. Notification Architecture & Truth in Telemetry

### Channel Governance
- **In-App Event Bus**: Connected and active (`DELIVERED`).
- **SMS Gateway**: Unconnected gateways explicitly report `NOT_CONFIGURED` with note *"Provider not configured"*. Zero fake delivery timestamps are generated.
- **WhatsApp Gateway**: Unconnected gateways report `NOT_CONFIGURED`.

### Controlled Message Templates
- **Government Alert**:
  > *“AniCare AI Alert: High-priority livestock health risk signal detected in [Area]. Priority: [P1], Signal: [Condition], Risk Score: [Score]. Field verification recommended. This is an early-warning signal and is not confirmation of an outbreak.”*
- **Farmer Advisory**:
  > *“AniCare AI: A health risk signal has been identified in your area. Please monitor your animals for unusual symptoms and contact a veterinarian if needed. AniCare AI provides decision support and does not independently confirm disease.”*

---

## 10. Operational Turnaround (SLA) Telemetry

Turnaround times are calculated strictly from actual ISO timestamps:
- $\text{Time to Acknowledge} = t_{\text{ALERT\_ACKNOWLEDGED}} - t_{\text{CREATED}}$ (Operational Target: $\le 30\text{ min}$)
- $\text{Time to Assign} = t_{\text{INVESTIGATION\_ASSIGNED}} - t_{\text{CREATED}}$ (Operational Target: $\le 60\text{ min}$)
- $\text{Time to Field Visit} = t_{\text{FIELD\_INVESTIGATION}} - t_{\text{CREATED}}$ (Operational Target: $\le 240\text{ min}$)
- $\text{Time to Lab Result} = t_{\text{LAB\_RESULT\_RECORDED}} - t_{\text{CREATED}}$
- $\text{Time to Resolution} = t_{\text{CASE\_CLOSED}} - t_{\text{CREATED}}$

---

## 11. Offline-First & Idempotent Synchronization

Field inspectors working in low-connectivity rural belts can log visits, specimens, and follow-ups offline. Each action carries a client-generated `idempotency_key`. When network connectivity is restored:
- Duplicate retries return the original record without duplicate document creation.
- Conflicting clinical decisions remain server-authoritative.

---

## 12. Verification & Testing Evidence

### Milestone 13 Test Suite (`backend/tests/test_milestone13_response.py`)
- **33 Dedicated Tests** covering:
  - Alert engine: P1 critical, P3 monitoring, deduplication, escalation.
  - RBAC: Farmer 403, Vet allowed, Field Officer allowed, Lab user allowed, Dept Officer allowed.
  - Investigation: Assignment, field findings, evidence validation, executable rejection.
  - Laboratory: Result recording, unauthorized rejection, non-autonomous routing to review.
  - Department: Review recording, authorized action permissions, farmer authorization rejection.
  - Notifications: In-app delivery, truth-in-telemetry unconfigured SMS/WhatsApp, deduplication.
  - Workflow: Follow-up tracking, case closure, critical case closure protection.
  - Integration: Milestone 12 hotspot link, Milestone 9C outbreak link, case reuse.
  - Offline: Idempotent retries, SLA duration metric calculations.
  - SIH Demonstration: 14-step automated scenario execution.

### Full Regression Suite
- **222 / 222 Automated Tests Passing (100% Pass Rate in 20.95s)**:
  - `test_ai_engine.py`: 7/7 PASS
  - `test_backend.py`: 10/10 PASS
  - `test_detection_api.py`: 10/10 PASS
  - `test_milestone6_multimodal.py`: 13/13 PASS
  - `test_milestone7_calibration.py`: 8/8 PASS
  - `test_milestone8a_external_validation.py`: 16/16 PASS
  - `test_milestone8b_model_improvement.py`: 16/16 PASS
  - `test_milestone9a_veterinary_workflow.py`: 8/8 PASS
  - `test_milestone9b_treatment_prevention.py`: 8/8 PASS
  - `test_milestone9c_outbreak_intelligence.py`: 8/8 PASS
  - `test_milestone9d_farmer_experience.py`: 8/8 PASS
  - `test_milestone10_offline_sync.py`: 20/20 PASS
  - `test_milestone11_ai_monitoring.py`: 22/22 PASS
  - `test_milestone12_geospatial.py`: 16/16 PASS
  - `test_milestone13_response.py`: 33/33 PASS
  - `test_vision_model.py`: 8/8 PASS

### Frontend Production Build
```text
vite v5.4.21 building for production...
✓ 1984 modules transformed.
dist/index.html                   1.28 kB │ gzip:   0.73 kB
dist/assets/index-D__3f7x6.css   68.71 kB │ gzip:  11.24 kB
dist/assets/index-8oxcY5o6.js   725.53 kB │ gzip: 178.83 kB
✓ built in 13.96s (0 errors)
```

---

## 13. SIH 2026 Presentation Guidance

When presenting to judges:

1. **Emphasize Decision Support Over Autonomous Action**:
   - *“AniCare converts early-warning risk signals into a controlled response workflow.”*
   - *“The platform helps authorities prioritize field investigation and track the response lifecycle.”*
   - *“Human veterinary and departmental authorization remains mandatory for clinical and government actions.”*
2. **Demonstrate the 14-Step Workflow**:
   - Use the **14-Step SIH Simulator** tab on `/response` to show judges how an initial Geospatial Hotspot leads to veterinary assignment, field specimen collection, PCR confirmation, human departmental sanction, and eventual risk downgrade.
3. **Showcase Truth in Telemetry**:
   - Highlight the gateway status showing `READY — PROVIDER NOT CONFIGURED` for SMS/WhatsApp, explaining that AniCare AI adheres to rigorous scientific and engineering integrity by never fabricating delivery receipts.
