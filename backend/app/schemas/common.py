from typing import Generic, TypeVar, Optional, Any, Dict
from pydantic import BaseModel, Field

T = TypeVar("T")

class ApiResponse(BaseModel, Generic[T]):
    success: bool = True
    message: str = "Operation completed successfully."
    data: Optional[T] = None
    meta: Optional[Dict[str, Any]] = None

class HealthStatusResponse(BaseModel):
    status: str = "healthy"
    version: str = "1.0.0"
    project_name: str = "AniCare AI"
    environment: str = "development"
    timestamp: str
    database: Dict[str, Any]
    demo_inference_mode: bool = True
