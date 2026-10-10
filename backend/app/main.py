import os
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.config import settings
from app.database import connect_to_mongo, close_mongo_connection
from app.routes import api_router
from app.services.animal_service import seed_default_animals_if_empty
from app.services.alert_service import seed_default_alerts_if_empty
from app.services.veterinary_service import seed_default_cases_if_empty
from app.services.outbreak_service import seed_default_outbreaks_if_empty
from app.services.reminder_service import seed_default_reminders_if_empty
from app.middleware.error_handler import (
    http_exception_handler,
    validation_exception_handler,
    unhandled_exception_handler
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle event management for the AniCare AI FastAPI backend.
    Initializes async MongoDB pool, ensures indexes, and pre-seeds baseline demo datasets.
    """
    # 1. Startup phase
    print("[STARTUP] Initializing AniCare AI Backend service...")
    await connect_to_mongo()
    
    # 2. Seed default registries if empty
    try:
        await seed_default_animals_if_empty()
        await seed_default_alerts_if_empty()
        await seed_default_cases_if_empty()
        await seed_default_outbreaks_if_empty()
        await seed_default_reminders_if_empty()
        print("[DATABASE] Baseline surveillance registries verified & seeded.")
    except Exception as e:
        print(f"[DATABASE] Note during seed initialization: {e}")


    yield

    # 3. Shutdown phase
    print("[SHUTDOWN] Shutting down AniCare AI Backend service...")
    await close_mongo_connection()

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=(
        "Production-grade REST API backend for AniCare AI — An AI-powered animal health "
        "and biosecurity early-warning platform engineered for SIH 2026 National Hackathon. "
        "Provides livestock registry management, multi-parameter disease screening, "
        "biosecurity alerts, and certified veterinary clinical workflows."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# 1. Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Configure Exception Handlers for Uniform Error Payloads
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)

# 3. Mount Static Uploads Folder
upload_path = Path(settings.UPLOAD_DIR)
upload_path.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(upload_path.resolve())), name="uploads")

# 4. Mount API Routers
app.include_router(api_router)

# 5. Service Discovery Root Endpoint
@app.get("/", tags=["System Discovery"])
async def root():
    return {
        "service": settings.PROJECT_NAME,
        "purpose": "SIH 2026 National Hackathon Prototyping Engine",
        "status": "operational",
        "api_documentation": "/docs",
        "redoc_documentation": "/redoc",
        "health_check": f"{settings.API_V1_STR}/health",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
