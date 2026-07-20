from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    username: str = Field(..., description="账号")
    password: str = Field(..., description="密码")


class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=2, max_length=50)
    email: str = Field(..., max_length=200)
    password: str = Field(..., min_length=6, max_length=100)
    display_name: str = Field(default="", max_length=50)
    department: str = Field(default="", max_length=100)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserInfo"


from datetime import datetime
from typing import Optional


class UserInfo(BaseModel):
    id: int
    username: str
    email: str
    display_name: str
    role: str
    department: str
    avatar_url: str
    is_active: bool = True
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
