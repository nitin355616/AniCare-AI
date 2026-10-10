# AniCare AI — System Architecture Specification

## 1. High-Level Architectural Vision

AniCare AI is built on a modern, decoupled, multi-tier architecture engineered for extreme reliability across resource-constrained rural environments. The system balances high-throughput edge data capture with strict statutory governance.

```mermaid
flowchart TD
    subgraph ClientLayer["Client & Field Tier (React 18 + PWA)"]
        UI_Farmer["Farmer Portal\n(Hindi / English / Voice / Offline)"]
        UI_Vet["Veterinary Care Interface\n(Clinical Review / Triage)"]
        UI_Command["Response Command Center\n(Alerts / Investigations / Actions)"]
        UI_Geo["Geospatial Intelligence Map\n(DBSCAN Hotspots / Risk Surfaces)"]
        IDB[("Client IndexedDB\nAction Queue & Offline Cache")]
        UI_Farmer <--> IDB
    end

    subgraph APILayer["Application & Microservices Tier (FastAPI / Python 3.12)"]
        GW["REST API Gateway\n(CORS / JWT / Rate Limiter)"]
        AuthSvc["Auth & RBAC Service\n(Farmer / Vet / Admin Roles)"]
        SyncEngine["Sync & Idempotency Engine\n(UUIDv4 Deduplication)"]
        DetectSvc["Multimodal Detection Service\n(EfficientNet-B0 ONNX + Symptoms)"]
        GeoSvc["Geospatial Clustering Service\n(DBSCAN eps=5km / SRI Calculator)"]
        RespSvc["Response Command Orchestrator\n(P1-P3 Alerts / Sample Custody)"]
        DriftSvc["Drift Surveillance Service\n(PSI Calculator / Shadow Engine)"]
    end

    subgraph DataLayer["Storage & Model Invariant Tier"]
        MongoDB[("MongoDB 7.0 Database\n2dsphere Spatial Index\nTTL Collections")]
        ONNX["Production Model Weights\nanicare_vision_bovine_v1.onnx\n(15.29 MB, tau=0.50, SHA-256 Verified)"]
        DataB[("Dataset B Storage\ndata/external/dataset_b/\nSTATUS: QUARANTINED")]
    end

    ClientLayer <-->|HTTPS / WSS| GW
    GW --> AuthSvc
    GW --> SyncEngine
    GW --> DetectSvc
    GW --> GeoSvc
    GW --> RespSvc
    GW --> DriftSvc

    SyncEngine <--> MongoDB
    DetectSvc <--> ONNX
    GeoSvc <--> MongoDB
    RespSvc <--> MongoDB
    DriftSvc <--> MongoDB
```

## 2. Core Architectural Principles

1. **Statutory Human-in-the-Loop:** In strict compliance with the Indian Veterinary Council Act, the AI system never acts as an autonomous diagnostic agent or prescribing entity. AI models output decision-support signals; all medical, pharmaceutical, and regulatory actions require verified veterinary credentials.
2. **Offline-First Fault Tolerance:** The field tier never assumes persistent network availability. All data entry forms function completely offline using browser IndexedDB storage and serialize payloads with UUID idempotency keys.
3. **Decoupled Geospatial Aggregation:** Animal-level records are spatially indexed using MongoDB `2dsphere` geometries. Real-time spatial clustering (DBSCAN) aggregates individual cases into village, block, and district early warning signals.
4. **Immutable Scientific Invariants:** Production model weights and validation benchmarks are protected against unauthorized modification. External datasets with unverified licensing (Dataset B) are kept quarantined under `PERMISSION_REQUIRED`.
