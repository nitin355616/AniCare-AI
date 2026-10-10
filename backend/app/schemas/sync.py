from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class SyncActionType(str, Enum):
    CREATE_HEALTH_OBSERVATION = "CREATE_HEALTH_OBSERVATION"
    REQUEST_DOCTOR_VISIT = "REQUEST_DOCTOR_VISIT"
    UPDATE_ANIMAL_OBSERVATION = "UPDATE_ANIMAL_OBSERVATION"
    CREATE_SCREENING_REQUEST = "CREATE_SCREENING_REQUEST"
    ACKNOWLEDGE_FOLLOW_UP = "ACKNOWLEDGE_FOLLOW_UP"

class SyncActionStatus(str, Enum):
    PENDING = "PENDING"
    SYNCING = "SYNCING"
    SYNCED = "SYNCED"
    ACCEPTED = "ACCEPTED"
    DUPLICATE = "DUPLICATE"
    FAILED = "FAILED"
    CONFLICT = "CONFLICT"
    CANCELLED = "CANCELLED"

class ConflictResolutionStrategy(str, Enum):
    SERVER_WINS = "SERVER_WINS"
    CLIENT_WINS = "CLIENT_WINS"
    KEEP_BOTH = "KEEP_BOTH"

class SyncActionItem(BaseModel):
    local_action_id: str = Field(..., description="Client-generated collision-resistant action UUID")
    idempotency_key: str = Field(..., description="Unique idempotency key preventing duplicate server application")
    action_type: SyncActionType = Field(..., description="Action category")
    entity_type: str = Field(..., description="Target entity type (e.g. health_record, animal, veterinary_case)")
    entity_id: Optional[str] = Field(None, description="Target entity identifier if applicable")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Action payload parameters")
    client_timestamp: str = Field(..., description="ISO 8601 timestamp when action was created offline")
    client_version: Optional[int] = Field(default=1, description="Entity version seen by client")

class SyncPushRequest(BaseModel):
    device_id: str = Field(..., description="Client device UUID")
    actions: List[SyncActionItem] = Field(..., description="List of queued offline actions to synchronize")

class SyncActionResult(BaseModel):
    local_action_id: str
    idempotency_key: str
    status: SyncActionStatus
    server_id: Optional[str] = None
    server_version: Optional[int] = None
    action_type: str
    entity_type: str
    entity_id: Optional[str] = None
    conflict_details: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    processed_at: str

class SyncPushResponse(BaseModel):
    success: bool
    server_timestamp: str
    processed_count: int
    accepted: List[SyncActionResult] = []
    duplicates: List[SyncActionResult] = []
    failed: List[SyncActionResult] = []
    conflicts: List[SyncActionResult] = []

class SyncPullRequest(BaseModel):
    device_id: str = Field(..., description="Client device UUID")
    since_cursor: Optional[str] = Field(None, description="ISO timestamp or cursor of last successful pull")
    entity_types: Optional[List[str]] = Field(None, description="Optional entity type filter")
    limit: Optional[int] = Field(default=100, ge=1, le=500, description="Max records per entity category")

class SyncPullResponse(BaseModel):
    server_timestamp: str
    next_cursor: str
    has_more: bool
    changes: Dict[str, List[Dict[str, Any]]]

class SyncStatusResponse(BaseModel):
    server_timestamp: str
    server_version: int = 1
    device_id: Optional[str] = None
    last_sync_timestamp: Optional[str] = None
    pending_conflicts_count: int = 0
    is_healthy: bool = True

class SyncConflictResolveRequest(BaseModel):
    conflict_id: str
    resolution_strategy: ConflictResolutionStrategy = Field(default=ConflictResolutionStrategy.SERVER_WINS)
    resolved_payload: Optional[Dict[str, Any]] = None

class SyncConflictResolveResponse(BaseModel):
    success: bool
    conflict_id: str
    applied_strategy: ConflictResolutionStrategy
    message: str
    resolved_at: str
