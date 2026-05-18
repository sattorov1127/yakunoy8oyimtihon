from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from app.core.enums import UserRole


class RegisterSchema(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    password: str
    role: UserRole = UserRole.CANDIDATE

    @field_validator("password")
    @classmethod
    def password_length(cls, v):
        if len(v) < 6:
            raise ValueError("Parol kamida 6 ta belgi bo'lishi kerak!")
        if len(v) > 72:
            raise ValueError("Parol 72 ta belgidan oshmasligi kerak!")
        return v

    class Config:
        use_enum_values = True


class LoginSchema(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    password: str


class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class ChangePasswordSchema(BaseModel):
    old_password: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def password_length(cls, v):
        if len(v) < 6:
            raise ValueError("Yangi parol kamida 6 ta belgi bo'lishi kerak!")
        if len(v) > 72:
            raise ValueError("Parol 72 ta belgidan oshmasligi kerak!")
        return v


class UserResponseSchema(BaseModel):
    id: int
    email: Optional[str] = None
    phone: Optional[str] = None
    role: str
    is_active: bool
    is_verified: bool

    class Config:
        from_attributes = True