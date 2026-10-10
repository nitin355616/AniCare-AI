# AniCare AI — Offline-First Architecture & Secure Synchronization

## 1. Rural Connectivity Strategy

Rural livestock farms frequently experience zero cellular connectivity. AniCare AI utilizes an offline-first architecture to guarantee zero data loss and eliminate duplicate submissions upon reconnection.

```mermaid
flowchart TD
    subgraph Client["Client Tier (Progressive Web App)"]
        UI["Farmer / Paravet Input Form"]
        IDB[("IndexedDB Local Store\n- Pending Actions\n- Animal Cache\n- Base64 Images")]
        Queue["Persistent Sync Queue\n(UUIDv4 Idempotency Keys)"]
        NetWatch["Network Listener\n(navigator.onLine + Heartbeat)"]

        UI --> IDB
        IDB --> Queue
        NetWatch --> Queue
    end

    subgraph Transport["Network Layer"]
        SyncBatch["POST /api/sync/batch-upload\n(Gzip Compressed JSON, Max 10 items)"]
        Backoff["Exponential Backoff Retry Engine\n(1s, 2s, 4s, 8s, Max 30s)"]
    end

    subgraph Backend["FastAPI Backend Tier"]
        SyncEndpoint["Batch Reconciliation Handler"]
        IdempCheck{"Idempotency Key Exists in DB?"}
        MongoInsert[("Atomic Insert / Upsert\n(MongoDB)")]
        AckResp["Return 200 OK Sync Manifest"]
    end

    Queue -->|Connection Restored| SyncBatch
    SyncBatch --> SyncEndpoint
    SyncEndpoint --> IdempCheck
    IdempCheck -- No --> MongoInsert
    IdempCheck -- Yes --> AckResp
    MongoInsert --> AckResp
    AckResp -->|Clear Uploaded Items| IDB
    SyncBatch -.->|Network Drop| Backoff
    Backoff -.-> Queue
```

## 2. Idempotency & Conflict Resolution

1. **Client-Side Generation:** Every action created offline is stamped with a cryptographic UUIDv4 token: `idempotency_key = "idemp_550e8400-e29b-41d4-a716-446655440000"`.
2. **Server-Side Deduplication:** The backend executes atomic `find_one_and_update` operations with upsert semantics keyed on `idempotency_key`. If the device resubmits the same record after an interrupted connection, the server acknowledges success without creating a duplicate record.
3. **Conflict Resolution:** In rare cases of concurrent field edits to the same animal record, the system follows a **Server-Authoritative, Most-Recent-Timestamp** policy: veterinarian edits always override unverified farmer updates.
