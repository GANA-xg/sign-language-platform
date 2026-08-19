from pydantic import BaseModel, EmailStr, Field

class UpdateProfileRequest(BaseModel):
    full_name: str | None = Field(None, max_length=150)
    email: EmailStr | None = None

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=6)

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=6)