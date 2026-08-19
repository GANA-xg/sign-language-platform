from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


# ============================================================
# Register
# ============================================================

class UserRegister(BaseModel):
    full_name: str = Field(..., max_length=150)
    email: EmailStr
    password: str = Field(..., min_length=6)
    # Matches what app/routers/auth.py reads: payload.requested_role
    requested_role: str | None = None


# ============================================================
# Login
# ============================================================

class UserLogin(BaseModel):
    email: EmailStr
    password: str
    # Matches what app/routers/auth.py reads: payload.role
    role: str | None = None


# ============================================================
# Refresh
# ============================================================

class RefreshTokenRequest(BaseModel):
    refresh_token: str


# ============================================================
# Responses
# ============================================================

class UserResponse(BaseModel):
    user_id: uuid.UUID
    full_name: str
    email: EmailStr
    roles: list[str]
    created_at: datetime

    class Config:
        from_attributes = True


class TokenPairResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse