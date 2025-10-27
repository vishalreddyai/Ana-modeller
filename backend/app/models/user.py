from typing import Optional, Any
from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator

class UserBase(BaseModel):
    email: str  # Changed from EmailStr to str to avoid validation issues
    username: str = Field(..., min_length=1, max_length=255)

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=128)

class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)

class User(UserBase):
    id: str
    token: Optional[str] = None
    refresh_token: Optional[str] = None
    is_active: Optional[bool] = True
    is_verified: Optional[bool] = False
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    last_login: Optional[str] = None
    failed_login_attempts: Optional[int] = 0
    account_locked_until: Optional[str] = None

    model_config = ConfigDict(
        from_attributes=True,
        extra='ignore',  # Ignore extra fields not defined in the model
        populate_by_name=True,
        arbitrary_types_allowed=True
    )

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    email: Optional[str] = None
