import logging
import traceback
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger("anicare.error_handler")

async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Handles standard HTTPException with consistent JSON structure."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "status_code": exc.status_code,
            "error": exc.detail if isinstance(exc.detail, str) else "HTTP Error",
            "detail": exc.detail,
            "details": exc.detail if not isinstance(exc.detail, str) else None,
            "path": str(request.url.path)
        }
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handles Pydantic validation errors with detailed parameter breakdowns."""
    formatted_errors = []
    for err in exc.errors():
        field_loc = " -> ".join([str(loc) for loc in err.get("loc", []) if loc != "body"])
        formatted_errors.append({
            "field": field_loc or "body",
            "message": err.get("msg", "Invalid parameter value"),
            "type": err.get("type", "value_error")
        })

    logger.warning(f"Validation failed for {request.method} {request.url.path}: {formatted_errors}")
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "status_code": 422,
            "error": "Request validation failed",
            "details": formatted_errors,
            "path": str(request.url.path)
        }
    )

async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catches unhandled errors and returns a 500 status without crashing the process."""
    err_str = str(exc)
    stack = traceback.format_exc()
    logger.error(f"Unhandled Exception on {request.method} {request.url.path}: {err_str}\n{stack}")

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "status_code": 500,
            "error": "Internal Server Error",
            "message": "An unexpected error occurred. Please consult backend server logs.",
            "path": str(request.url.path)
        }
    )
