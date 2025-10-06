from datetime import timedelta
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, Field
from ..models.user import UserCreate, UserLogin, User, Token
from ..services.user_service import UserService
from ..auth import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, send_password_reset_email

router = APIRouter()
user_service = UserService()

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordReset(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8, max_length=128)

@router.post("/signup", response_model=User, status_code=status.HTTP_201_CREATED)
async def signup(user: UserCreate):
    try:
        return user_service.create_user(user)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/request-password-reset", status_code=status.HTTP_200_OK)
async def request_password_reset(request: PasswordResetRequest):
    user_data = user_service.get_user_by_email(request.email)
    if not user_data:
        # For security, don't reveal if the email is not registered
        raise HTTPException(
            status_code=status.HTTP_200_OK,
            detail="If an account with that email exists, a password reset link will be sent."
        )
    
    # Generate a password reset token
    reset_token_expires = timedelta(minutes=30) # Token valid for 30 minutes
    reset_token = create_access_token(
        data={"sub": str(request.email), "type": "password_reset"},
        expires_delta=reset_token_expires
    )
    
    await send_password_reset_email(str(request.email), reset_token)
    
    return {"message": "If an account with that email exists, a password reset link will be sent."}

@router.post("/reset-password", status_code=status.HTTP_200_OK)
async def reset_password(reset: PasswordReset):
    try:
        payload = jwt.decode(reset.token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        token_type: str = payload.get("type")
        
        if email is None or token_type != "password_reset":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired password reset token"
            )
        
        user_service.update_user_password(EmailStr(email), reset.new_password)
        return {"message": "Password has been reset successfully."}
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired password reset token"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = user_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Keep the /signin endpoint for direct login with UserLogin model if needed,
# but the /token endpoint is preferred for OAuth2PasswordRequestForm
@router.post("/signin", response_model=User)
async def signin(user_login: UserLogin):
    try:
        user = user_service.authenticate_user(str(user_login.email), user_login.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        # For direct signin, we might not return a token directly,
        # but the user object. If a token is required here,
        # the logic from /token should be adapted.
        return user
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
