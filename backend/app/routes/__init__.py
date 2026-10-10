from fastapi import APIRouter
from app.routes.health import router as health_router
from app.routes.auth import router as auth_router
from app.routes.animals import router as animals_router
from app.routes.health_records import router as health_records_router
from app.routes.detection import router as detection_router, disease_router
from app.routes.veterinary import router as veterinary_router
from app.routes.alerts import router as alerts_router
from app.routes.epidemiology import router as epidemiology_router
from app.routes.evaluation import router as evaluation_router
from app.routes.outbreaks import router as outbreaks_router
from app.routes.farmer import router as farmer_router
from app.routes.sync import router as sync_router
from app.routes.ai_monitoring import router as ai_monitoring_router
from app.routes.ai_feedback import router as ai_feedback_router
from app.routes.geospatial import router as geospatial_router
from app.routes.response import router as response_router
from app.routes.demo import router as demo_router
from app.routes.history import router as history_router
from app.routes.reminders import router as reminders_router
from app.routes.datasets import router as datasets_router
from app.routes.models import router as models_router

api_router = APIRouter(prefix="/api")

api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(animals_router)
api_router.include_router(health_records_router)
api_router.include_router(detection_router)
api_router.include_router(disease_router)
api_router.include_router(history_router)
api_router.include_router(reminders_router)
api_router.include_router(veterinary_router)
api_router.include_router(alerts_router)
api_router.include_router(epidemiology_router)
api_router.include_router(evaluation_router)
api_router.include_router(outbreaks_router)
api_router.include_router(farmer_router)
api_router.include_router(sync_router)
api_router.include_router(ai_monitoring_router)
api_router.include_router(ai_feedback_router)
api_router.include_router(geospatial_router)
api_router.include_router(response_router)
api_router.include_router(demo_router)
api_router.include_router(datasets_router)
api_router.include_router(models_router)

__all__ = ["api_router"]


