from enum import Enum
from typing import Optional
from pydantic import BaseModel, EmailStr, Field

class UserRole(str, Enum):
    FARMER = "farmer"
    VETERINARIAN = "veterinarian"
    ADMIN = "admin"

class UserRegister(BaseModel):
    email: EmailStr = Field(..., examples=["vet.patel@anicare.org"])
    password: str = Field(..., min_length=6, description="Password must be at least 6 characters.")
    full_name: str = Field(..., min_length=2, examples=["Dr. Rajesh Patel"])
    role: UserRole = Field(default=UserRole.FARMER)
    phone: Optional[str] = Field(None, examples=["+91 98250 44102"])
    location: Optional[str] = Field(None, examples=["Anand District, Gujarat"])

class UserLogin(BaseModel):
    email: EmailStr = Field(..., examples=["vet.patel@anicare.org"])
    password: str = Field(...)

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    role: UserRole
    phone: Optional[str] = None
    location: Optional[str] = None
    created_at: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in_minutes: int
    user: UserResponse
