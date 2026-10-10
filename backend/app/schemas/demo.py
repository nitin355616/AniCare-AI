"""
AniCare AI — SIH National Demo & Jury Packaging Schemas
Milestone 14: Demo Health, Session Isolation, One-Click Seeding & Reset.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

SAFETY_DISCLAIMER = (
    "SIH DEMONSTRATION MODE: All data in this session is synthetic and intended "
    "for presentation and evaluation. AI-generated risk signals provide decision support; "
    "veterinary examination and statutory department authorization remain human-controlled."
)


class DemoHealthResponse(BaseModel):
    backend: bool = True
    database: bool = True
    demo_seeded: bool = True
    production_model_available: bool = True
    frontend_ready: bool = True
    production_model_sha256: str = "594d42c7d12fd32a4d22dc7f4cd32156162cb6170e05a432b2010d306f5f4f8d"
    operating_threshold: float = 0.50
    model_size_mb: float = 15.29
    total_backend_tests: int = 222
    tests_passing: int = 222
    timestamp: str
    disclaimer: str = SAFETY_DISCLAIMER


class DemoSeedResponse(BaseModel):
    status: str = "seeded"
    session_id: str
    records_created: Dict[str, int]
    timestamp: str
    message: str
    disclaimer: str = SAFETY_DISCLAIMER


class DemoResetResponse(BaseModel):
    status: str = "reset_complete"
    session_id: str
    records_removed: Dict[str, int]
    timestamp: str
    message: str
    disclaimer: str = SAFETY_DISCLAIMER


class DemoStepDetail(BaseModel):
    step_id: int
    title: str
    subtitle: str
    route_target: str
    status: str = "PENDING"
    actor: str
    role: str
    description: str
    data_payload: Dict[str, Any] = Field(default_factory=dict)
    timestamp: Optional[str] = None


class DemoStateResponse(BaseModel):
    session_id: str
    current_step: int
    total_steps: int = 10
    is_active: bool = True
    steps: List[DemoStepDetail]
    disclaimer: str = SAFETY_DISCLAIMER
