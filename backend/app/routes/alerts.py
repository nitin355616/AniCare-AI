from typing import Optional
from fastapi import APIRouter, Query, status
from app.schemas.alert import (
    AlertCreate,
    AlertAcknowledgeRequest,
    AlertResponse,
    AlertListResponse
)
from app.services.alert_service import (
    get_alerts,
    create_alert,
    acknowledge_alert
)

router = APIRouter(prefix="/alerts", tags=["Biosecurity Alerts & Outbreaks"])

@router.get("", response_model=AlertListResponse)
async def api_get_alerts(
    alert_type: Optional[str] = Query(None, description="Filter by type: critical, disease-risk, follow-up, vaccination, preventive"),
    severity: Optional[str] = Query(None, description="Filter by severity: Critical, High, Medium, Low"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status: Active, Acknowledged, Resolved"),
    limit: int = Query(50, ge=1, le=200),
    skip: int = Query(0, ge=0)
):
    """
    Retrieves biosecurity and animal clinical alerts with multi-dimensional filtering.
    """
    return await get_alerts(alert_type=alert_type, severity=severity, status_filter=status_filter, limit=limit, skip=skip)

@router.post("", response_model=AlertResponse, status_code=status.HTTP_201_CREATED)
async def api_create_alert(data: AlertCreate):
    """
    Triggers an early warning or veterinary reminder alert.
    """
    return await create_alert(data)

@router.put("/{alert_id}/acknowledge", response_model=AlertResponse)
async def api_acknowledge_alert(alert_id: str, data: AlertAcknowledgeRequest):
    """
    Marks an alert as acknowledged by a veterinarian or farm officer.
    """
    return await acknowledge_alert(alert_id, data)
