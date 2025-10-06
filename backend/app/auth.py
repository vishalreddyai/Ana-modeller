from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status

# Configuration for JWT
SECRET_KEY = "YOUR_SECRET_KEY"  # TODO: Change this to a strong, random key in production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

# Placeholder for email sending
async def send_password_reset_email(email: str, token: str):
    reset_link = f"http://localhost:3000/reset-password?token={token}"
    print(f"--- Password Reset Email ---")
    print(f"To: {email}")
    print(f"Subject: Password Reset Request")
    print(f"Body: Click the following link to reset your password: {reset_link}")
    print(f"----------------------------")
    # TODO: Integrate with an actual email sending service (e.g., SendGrid, Mailgun)
