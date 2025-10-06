from typing import Optional
from pydantic import BaseModel, EmailStr, Field

class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=1, max_length=255)

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=128)

class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)

class User(UserBase):
    id: str
    password: Optional[str] = None  # This will store the hashed password
    token: Optional[str] = None # Add token field for JWT

    class Config:
        from_attributes = True
        json_encoders = {
            EmailStr: lambda v: str(v)  # Convert EmailStr to string for JSON serialization
        }

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    email: Optional[str] = None
