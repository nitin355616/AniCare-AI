import datetime
import uuid
from typing import Optional
from fastapi import HTTPException, status
from app.database import get_users_collection
from app.utils.security import hash_password, verify_password, create_access_token
from app.schemas.auth import UserRegister, UserLogin, UserResponse, TokenResponse, UserRole
from app.config import settings

async def register_user(data: UserRegister) -> TokenResponse:
    users_col = get_users_collection()
    if users_col is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection is unavailable."
        )

    # Check existing email
    existing = await users_col.find_one({"email": data.email.lower()})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email address already exists."
        )

    user_id = f"USR-{uuid.uuid4().hex[:8].upper()}"
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
    hashed_pwd = hash_password(data.password)

    user_doc = {
        "id": user_id,
        "email": data.email.lower(),
        "password_hash": hashed_pwd,
        "full_name": data.full_name,
        "role": data.role.value,
        "phone": data.phone,
        "location": data.location,
        "created_at": now_iso,
        "updated_at": now_iso
    }

    await users_col.insert_one(user_doc)

    user_res = UserResponse(
        id=user_id,
        email=user_doc["email"],
        full_name=user_doc["full_name"],
        role=UserRole(user_doc["role"]),
        phone=user_doc["phone"],
        location=user_doc["location"],
        created_at=user_doc["created_at"]
    )

    access_token = create_access_token({
        "sub": user_id,
        "email": user_doc["email"],
        "role": user_doc["role"],
        "name": user_doc["full_name"]
    })

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        user=user_res
    )

async def authenticate_user(data: UserLogin) -> TokenResponse:
    users_col = get_users_collection()
    if users_col is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection is unavailable."
        )

    user_doc = await users_col.find_one({"email": data.email.lower()})
    if not user_doc or not verify_password(data.password, user_doc.get("password_hash", "")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )

    user_res = UserResponse(
        id=user_doc["id"],
        email=user_doc["email"],
        full_name=user_doc["full_name"],
        role=UserRole(user_doc["role"]),
        phone=user_doc.get("phone"),
        location=user_doc.get("location"),
        created_at=user_doc["created_at"]
    )

    access_token = create_access_token({
        "sub": user_doc["id"],
        "email": user_doc["email"],
        "role": user_doc["role"],
        "name": user_doc["full_name"]
    })

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        user=user_res
    )

async def get_user_by_id(user_id: str) -> Optional[UserResponse]:
    users_col = get_users_collection()
    if users_col is None:
        return None
    doc = await users_col.find_one({"id": user_id})
    if not doc:
        return None
    return UserResponse(
        id=doc["id"],
        email=doc["email"],
        full_name=doc["full_name"],
        role=UserRole(doc["role"]),
        phone=doc.get("phone"),
        location=doc.get("location"),
        created_at=doc["created_at"]
    )
