import datetime
from fastapi import APIRouter
from app.database import ping_database
from app.config import settings
from app.schemas.common import HealthStatusResponse

router = APIRouter(tags=["Health Check"])

@router.get("/health", response_model=HealthStatusResponse)
async def check_health():
    """
    Returns backend health status, application version,
    and live MongoDB database connectivity status with latency.
    """
    db_status = await ping_database()
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
    
    overall_status = "healthy" if db_status.get("connected") else "degraded"

    return HealthStatusResponse(
        status=overall_status,
        version=settings.VERSION,
        project_name=settings.PROJECT_NAME,
        environment=settings.ENVIRONMENT,
        timestamp=now_iso,
        database=db_status,
        demo_inference_mode=True
    )
