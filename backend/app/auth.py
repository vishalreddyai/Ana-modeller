import os
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Union
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import ValidationError

# Security configurations
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "a_very_secret_key_that_should_be_in_env_file")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Access token validity
REFRESH_TOKEN_EXPIRE_DAYS = 7     # Refresh token validity
PASSWORD_RESET_TOKEN_EXPIRE_HOURS = 1

# Token types for different purposes
class TokenType:
    ACCESS = "access"
    REFRESH = "refresh"
    PASSWORD_RESET = "password_reset"

# Password hashing context with recommended settings
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12  # Adjust based on your security requirements
)

# Token blacklist (in production, use Redis or a database)
token_blacklist = set()

class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True, token_type: str = TokenType.ACCESS):
        self.token_type = token_type
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> str:
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid authorization code."
            )
        
        if not credentials.scheme == "Bearer":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid authentication scheme."
            )
        
        token = credentials.credentials
        if is_token_blacklisted(token):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked"
            )
            
        return token

def create_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None,
    token_type: str = TokenType.ACCESS
) -> str:
    """Create a JWT token with the given data and expiration."""
    to_encode = data.copy()
    now = datetime.utcnow()
    
    if expires_delta:
        expire = now + expires_delta
    else:
        if token_type == TokenType.REFRESH:
            expire = now + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        elif token_type == TokenType.PASSWORD_RESET:
            expire = now + timedelta(hours=PASSWORD_RESET_TOKEN_EXPIRE_HOURS)
        else:  # access token
            expire = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Add standard claims
    to_encode.update({
        "exp": expire,
        "iat": now,
        "type": token_type,
        "jti": secrets.token_urlsafe(16)  # Unique token identifier
    })
    
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> Dict[str, Any]:
    """Decode and validate a JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

def create_access_token(email: str) -> str:
    """Create an access token for the given email."""
    return create_token(
        data={"sub": email},
        token_type=TokenType.ACCESS
    )

def create_refresh_token(email: str) -> str:
    """Create a refresh token for the given email."""
    return create_token(
        data={"sub": email},
        token_type=TokenType.REFRESH
    )

def create_password_reset_token(email: str) -> str:
    """Create a password reset token for the given email."""
    return create_token(
        data={"sub": email},
        token_type=TokenType.PASSWORD_RESET
    )

def verify_token(token: str, token_type: str = TokenType.ACCESS) -> Dict[str, Any]:
    """Verify a JWT token and return its payload if valid."""
    try:
        payload = decode_token(token)
        
        # Check token type
        if payload.get("type") != token_type:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Token type mismatch, expected {token_type}"
            )
            
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

def get_current_user(token: str = Depends(JWTBearer())) -> Dict[str, Any]:
    """Dependency to get the current user from the JWT token."""
    try:
        payload = verify_token(token, TokenType.ACCESS)
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        return {"email": email, "token": token}
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

def revoke_token(token: str) -> None:
    """Add a token to the blacklist."""
    # In production, store this in Redis with an expiration time
    token_blacklist.add(token)

def is_token_blacklisted(token: str) -> bool:
    """Check if a token is blacklisted."""
    return token in token_blacklist

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Generate a password hash."""
    return pwd_context.hash(password)

async def send_password_reset_email(email: str, token: str) -> None:
    """Send a password reset email."""
    reset_link = f"http://localhost:3000/reset-password?token={token}"
    
    # In production, integrate with an email service like SendGrid, Mailgun, etc.
    print("\n" + "="*80)
    print(f"PASSWORD RESET EMAIL")
    print("-" * 40)
    print(f"To: {email}")
    print(f"Subject: Password Reset Request")
    print("\nBody:")
    print(f"You requested a password reset. Click the link below to reset your password:")
    print(f"{reset_link}")
    print(f"\nThis link will expire in {PASSWORD_RESET_TOKEN_EXPIRE_HOURS} hours.")
    print("="*80 + "\n")
