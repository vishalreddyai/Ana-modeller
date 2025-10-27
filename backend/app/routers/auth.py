from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, status, Depends, Request, Response
from fastapi.security import OAuth2PasswordRequestForm, HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, Field, validator, ValidationError
from typing import Optional

from ..models.user import UserCreate, UserLogin, User, Token, TokenData
from ..services.user_service import UserService
from ..auth import (
    create_access_token,
    create_refresh_token,
    create_password_reset_token,
    verify_token,
    TokenType,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS,
    send_password_reset_email,
    revoke_token,
    JWTBearer
)

router = APIRouter()
user_service = UserService()
security = HTTPBearer()

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordReset(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8, max_length=128)
    current_password: Optional[str] = Field(None, min_length=8, max_length=128)
    
    @validator('new_password')
    def validate_password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one number')
        if not any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?/' for c in v):
            raise ValueError('Password must contain at least one special character')
        return v

@router.post("/signup", response_model=User, status_code=status.HTTP_201_CREATED)
async def signup(user: UserCreate):
    """
    Register a new user.
    
    - **email**: Must be a valid email address
    - **username**: Must be between 3 and 50 characters
    - **password**: Must be at least 8 characters long, containing at least one uppercase,
      one lowercase, one number and one special character
    """
    try:
        user_data = user_service.create_user(user)
        return User.model_validate(user_data)
    except HTTPException as e:
        raise e
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the user"
        )

@router.post("/request-password-reset", status_code=status.HTTP_200_OK)
async def request_password_reset(request: PasswordResetRequest):
    """
    Request a password reset email.
    
    This will send an email with a password reset link if the email is registered.
    For security reasons, we don't reveal if the email exists or not.
    """
    user_data = user_service.get_user_by_email(request.email)
    if not user_data:
        # For security, don't reveal if the email is not registered
        return {
            "message": "If an account with that email exists, a password reset link will be sent."
        }
    
    # Generate a password reset token
    reset_token = create_password_reset_token(str(request.email))
    
    # Send the password reset email
    await send_password_reset_email(str(request.email), reset_token)
    
    return {
        "message": "If an account with that email exists, a password reset link will be sent."
    }

# Alias to match frontend endpoint name
@router.post("/forgot-password", status_code=status.HTTP_200_OK)
async def forgot_password(request: PasswordResetRequest):
    return await request_password_reset(request)

@router.post("/reset-password", status_code=status.HTTP_200_OK)
async def reset_password(reset: PasswordReset):
    """
    Reset a user's password using a valid reset token.
    
    - **token**: The password reset token from the email
    - **new_password**: The new password
    - **current_password**: Required if the user is already logged in
    """
    try:
        # Verify the reset token
        payload = verify_token(reset.token, TokenType.PASSWORD_RESET)
        email = payload.get("sub")
        
        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid password reset token"
            )
        
        # Update the user's password
        user_service.update_user_password(
            email=email,
            new_password=reset.new_password,
            current_password=reset.current_password
        )
        
        return {"message": "Password has been reset successfully."}
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired password reset token"
        )

@router.post("/token", response_model=Token)
async def login_for_access_token(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    OAuth2 compatible token login, get an access token for future requests.
    
    - **username**: The user's email
    - **password**: The user's password
    
    Returns:
    - **access_token**: JWT access token
    - **refresh_token**: JWT refresh token
    - **token_type**: Always "bearer"
    - **expires_in**: Token expiration time in seconds
    """
    try:
        # Authenticate the user
        user_data, access_token, refresh_token = user_service.authenticate_user(
            email=form_data.username,
            password=form_data.password
        )
        
        # Set HTTP-only cookies for better security (optional)
        response.set_cookie(
            key="access_token",
            value=f"Bearer {access_token}",
            httponly=True,
            max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            secure=False,  # Set to True in production with HTTPS
            samesite="lax"
        )
        
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
            secure=False,  # Set to True in production with HTTPS
            samesite="lax"
        )
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.post("/refresh-token", response_model=Token)
async def refresh_access_token(
    request: Request,
    response: Response,
    refresh_token: str = Depends(security)
):
    """
    Get a new access token using a refresh token.
    
    - **refresh_token**: A valid refresh token
    
    Returns:
    - **access_token**: New JWT access token
    - **refresh_token**: New JWT refresh token
    - **token_type**: Always "bearer"
    - **expires_in**: Token expiration time in seconds
    """
    try:
        # Get refresh token from header or cookie
        if isinstance(refresh_token, HTTPAuthorizationCredentials):
            refresh_token = refresh_token.credentials
            
        # Refresh the tokens
        tokens = user_service.refresh_tokens(refresh_token)
        
        # Update cookies
        response.set_cookie(
            key="access_token",
            value=f"Bearer {tokens['access_token']}",
            httponly=True,
            max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            secure=False,  # Set to True in production with HTTPS
            samesite="lax"
        )
        
        response.set_cookie(
            key="refresh_token",
            value=tokens['refresh_token'],
            httponly=True,
            max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
            secure=False,  # Set to True in production with HTTPS
            samesite="lax"
        )
        
        return {
            "access_token": tokens["access_token"],
            "refresh_token": tokens["refresh_token"],
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    response: Response,
    token: str = Depends(security)
):
    """
    Log out the current user by revoking their access token.
    """
    if isinstance(token, HTTPAuthorizationCredentials):
        token = token.credentials
    
    # Revoke the token
    result = user_service.logout(token)
    
    # Clear cookies
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    
    return result

@router.post("/signin", response_model=User)
async def signin(
    response: Response,
    user: UserLogin
):
    """
    Alternative login endpoint that accepts a JSON body.
    
    - **email**: The user's email
    - **password**: The user's password
    
    Returns the user object with tokens.
    """
    try:
        # Authenticate the user
        user_data, access_token, refresh_token = user_service.authenticate_user(
            email=user.email,
            password=user.password
        )
        
        # Set HTTP-only cookies for better security (optional)
        response.set_cookie(
            key="access_token",
            value=f"Bearer {access_token}",
            httponly=True,
            max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            secure=False,  # Set to True in production with HTTPS
            samesite="lax"
        )
        
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
            secure=False,  # Set to True in production with HTTPS
            samesite="lax"
        )
        
        # Add tokens to the user data
        user_data["token"] = access_token
        user_data["refresh_token"] = refresh_token
        
        # Use model_validate for proper Pydantic v2 validation
        return User.model_validate(user_data)
        
    except HTTPException as e:
        raise e
    except Exception as e:
        import traceback
        print(f"Error in signin: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while signing in: {str(e)}"
        )
