from typing import Optional, Dict, Any
from fastapi import APIRouter, status, Depends
from app.schemas.sync import (
    SyncPushRequest,
    SyncPushResponse,
    SyncPullRequest,
    SyncPullResponse,
    SyncStatusResponse,
    SyncConflictResolveRequest,
    SyncConflictResolveResponse
)
from app.services.sync_service import (
    process_sync_push,
    process_sync_pull,
    get_sync_status_summary,
    resolve_conflict_record
)
from app.routes.veterinary import get_optional_user

router = APIRouter(prefix="/sync", tags=["Offline Synchronization & Queue"])

@router.post("/push", response_model=SyncPushResponse, status_code=status.HTTP_200_OK)
async def api_sync_push(
    request: SyncPushRequest,
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """
    Synchronizes a batch of queued offline actions with idempotency checks,
    ownership verification, and conflict detection.
    """
    return await process_sync_push(request=request, current_user=current_user)

@router.post("/pull", response_model=SyncPullResponse, status_code=status.HTTP_200_OK)
async def api_sync_pull(
    request: SyncPullRequest,
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """
    Incrementally fetches server-side changes modified since the client's last sync cursor.
    """
    return await process_sync_pull(request=request, current_user=current_user)

@router.get("/status", response_model=SyncStatusResponse)
async def api_sync_status(
    device_id: Optional[str] = None,
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """
    Returns server health, monotonic sync version, and server timestamp for reachability checks.
    """
    return await get_sync_status_summary(device_id=device_id, current_user=current_user)

@router.post("/resolve", response_model=SyncConflictResolveResponse)
async def api_sync_resolve(
    request: SyncConflictResolveRequest,
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """
    Resolves client-server sync conflicts respecting veterinary clinical authority.
    """
    return await resolve_conflict_record(request=request, current_user=current_user)
