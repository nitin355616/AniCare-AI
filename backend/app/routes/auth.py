from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.auth import UserRegister, UserLogin, UserResponse, TokenResponse
from app.services.auth_service import register_user, authenticate_user, get_user_by_id
from app.utils.security import get_current_user_payload

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def api_register(data: UserRegister):
    """
    Registers a new user (farmer, veterinarian, or admin).
    Generates salted password hash and returns JWT authorization bearer token.
    """
    return await register_user(data)

@router.post("/login", response_model=TokenResponse)
async def api_login(data: UserLogin):
    """
    Authenticates existing user with email and password.
    Returns access token on valid credentials.
    """
    return await authenticate_user(data)

@router.get("/me", response_model=UserResponse)
async def api_get_current_user(payload: dict = Depends(get_current_user_payload)):
    """
    Returns the authenticated user profile based on the JWT Bearer token.
    """
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload.")
    user = await get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User account not found.")
    return user
