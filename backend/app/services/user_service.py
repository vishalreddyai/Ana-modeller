import json
import uuid
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
from pydantic import ValidationError
from fastapi import HTTPException, status, Depends
from ..models.user import UserCreate, User, Token
from ..auth import (
    get_password_hash, 
    verify_password, 
    create_access_token,
    create_refresh_token,
    verify_token,
    revoke_token,
    JWTBearer,
    TokenType,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from jose import JWTError

# Password requirements
PASSWORD_MIN_LENGTH = 8
PASSWORD_MAX_LENGTH = 128
PASSWORD_REGEX = re.compile(
    r'^(?=.*[a-z])(?=.*[A-Z]'  # At least one lowercase and one uppercase
    r')(?=.*\d)'                # At least one digit
    r'(?=.*[!@#$%^&*()_+\-=\[\]{};\'\"|,.<>?/])'  # At least one special char
    r'.*$'
)

class UserService:
    def __init__(self):
        self.users_file = Path(__file__).parent.parent / "data" / "users.json"
        self._ensure_users_file_exists()

    def _ensure_users_file_exists(self):
        if not self.users_file.exists():
            self.users_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.users_file, 'w', encoding='utf-8') as f:
                json.dump({"users": []}, f, indent=2)

    def _load_users(self) -> list[Dict[str, Any]]:
        try:
            with open(self.users_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("users", [])
        except FileNotFoundError:
            self._ensure_users_file_exists()
            return []
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error reading users data"
            )

    def _save_users(self, users: list) -> None:
        try:
            with open(self.users_file, 'w', encoding='utf-8') as f:
                json.dump({"users": users}, f, indent=4, ensure_ascii=False)
        except IOError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error saving user data"
            )

    def _validate_password(self, password: str) -> None:
        """Validate password against security requirements."""
        if len(password) < PASSWORD_MIN_LENGTH:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Password must be at least {PASSWORD_MIN_LENGTH} characters long"
            )
            
        if len(password) > PASSWORD_MAX_LENGTH:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Password must be at most {PASSWORD_MAX_LENGTH} characters long"
            )
            
        if not PASSWORD_REGEX.match(password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Password must contain at least one uppercase letter, "
                    "one lowercase letter, one number and one special character"
                )
            )

    def create_user(self, user: UserCreate) -> Dict[str, Any]:
        """Create a new user with the given information."""
        users = self._load_users()
        
        # Check if user already exists
        if any(u["email"].lower() == user.email.lower() for u in users):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
            
        # Validate password strength
        self._validate_password(user.password)
        
        # Hash the password
        hashed_password = get_password_hash(user.password)
        
        # Create new user with UUID and timestamps
        now = datetime.utcnow().isoformat()
        new_user = {
            "id": str(uuid.uuid4()),
            "email": user.email.lower().strip(),
            "username": user.username.strip(),
            "password": hashed_password,
            "is_active": True,
            "is_verified": False,  # Email verification can be implemented later
            "created_at": now,
            "updated_at": now,
            "last_login": None,
            "failed_login_attempts": 0,
            "account_locked_until": None
        }
        
        users.append(new_user)
        self._save_users(users)
        
        # Return user without sensitive data
        return {k: v for k, v in new_user.items() if k != 'password'}

    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get a user by email (case-insensitive)."""
        users = self._load_users()
        email_lower = email.lower().strip()
        for user in users:
            if user["email"].lower() == email_lower:
                return user  # Return full user data including password hash for internal use
        return None

    def authenticate_user(self, email: str, password: str) -> Tuple[Dict[str, Any], str, str]:
        """
        Authenticate a user with email and password.
        Returns a tuple of (user_data, access_token, refresh_token) if successful, raises HTTPException otherwise.
        """
        # Normalize email for comparison
        normalized_email = email.lower().strip()
        
        user_data = self.get_user_by_email(normalized_email)
        if not user_data:
            # Don't reveal if user exists for security
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
            
        # Check if account is locked
        if user_data.get("account_locked_until"):
            locked_until = datetime.fromisoformat(user_data["account_locked_until"])
            if datetime.utcnow() < locked_until:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Account is temporarily locked due to too many failed login attempts"
                )
            else:
                # Reset lock if expired
                user_data["account_locked_until"] = None
                user_data["failed_login_attempts"] = 0
        
        # Verify password with graceful legacy plaintext handling
        stored_password_value = user_data.get("password", "")
        password_is_valid = False
        try:
            password_is_valid = verify_password(password, stored_password_value)
        except Exception:
            # If stored value is not a valid hash (legacy plaintext), compare directly
            password_is_valid = stored_password_value == password
            if password_is_valid:
                # Upgrade to hashed password on successful plaintext match
                users_to_upgrade = self._load_users()
                for i, u in enumerate(users_to_upgrade):
                    if u["id"] == user_data["id"]:
                        users_to_upgrade[i]["password"] = get_password_hash(password)
                        users_to_upgrade[i]["updated_at"] = datetime.utcnow().isoformat()
                        self._save_users(users_to_upgrade)
                        user_data.update(users_to_upgrade[i])
                        break

        if not password_is_valid:
            # Update failed login attempts
            users = self._load_users()
            for i, u in enumerate(users):
                if u["id"] == user_data["id"]:
                    users[i]["failed_login_attempts"] = user_data.get("failed_login_attempts", 0) + 1
                    
                    # Lock account after 5 failed attempts for 15 minutes
                    if users[i]["failed_login_attempts"] >= 5:
                        lock_time = datetime.utcnow() + timedelta(minutes=15)
                        users[i]["account_locked_until"] = lock_time.isoformat()
                        self._save_users(users)
                        raise HTTPException(
                            status_code=status.HTTP_403_FORBIDDEN,
                            detail="Too many failed login attempts. Account locked for 15 minutes."
                        )
                    
                    self._save_users(users)
                    break
            
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        # Reset failed login attempts on successful login
        users = self._load_users()
        for i, u in enumerate(users):
            if u["id"] == user_data["id"]:
                users[i]["failed_login_attempts"] = 0
                users[i]["last_login"] = datetime.utcnow().isoformat()
                users[i]["account_locked_until"] = None
                self._save_users(users)
                user_data.update(users[i])
                break
        
        # Generate tokens
        access_token = create_access_token(user_data["email"])
        refresh_token = create_refresh_token(user_data["email"])
        
        # Return user data (without password) and tokens
        user_data.pop("password", None)
        
        return user_data, access_token, refresh_token

    def update_user_password(self, email: str, new_password: str, current_password: str = None) -> Dict[str, Any]:
        """Update a user's password.
        
        Args:
            email: The user's email
            new_password: The new password
            current_password: The current password (required if user is changing their own password)
            
        Returns:
            Dictionary with user data and new tokens
        """
        users = self._load_users()
        user_data = None
        user_index = -1
        
        # Find the user
        for i, user in enumerate(users):
            if user["email"].lower() == str(email).lower():
                user_data = user
                user_index = i
                break
                
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
            
        # If current_password is provided, verify it
        if current_password is not None:
            if not verify_password(current_password, user_data.get("password", "")):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Current password is incorrect"
                )
        
        # Validate new password
        self._validate_password(new_password)
        
        # Update password
        users[user_index]["password"] = get_password_hash(new_password)
        users[user_index]["updated_at"] = datetime.utcnow().isoformat()
        
        # Save changes
        self._save_users(users)
        
        # Generate new tokens
        access_token = create_access_token(user_data["email"])
        refresh_token = create_refresh_token(user_data["email"])
        
        # Return updated user data without password
        user_data = users[user_index].copy()
        user_data.pop("password", None)
        user_data["tokens"] = {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
        return user_data

    def refresh_tokens(self, refresh_token: str) -> Dict[str, str]:
        """Generate new access and refresh tokens using a valid refresh token."""
        try:
            # Verify the refresh token
            payload = verify_token(refresh_token, TokenType.REFRESH)
            email = payload.get("sub")
            
            if not email:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid refresh token"
                )
                
            # Check if user exists
            user_data = self.get_user_by_email(email)
            if not user_data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
                
            # Generate new tokens
            new_access_token = create_access_token(email)
            new_refresh_token = create_refresh_token(email)
            
            # Revoke the old refresh token
            revoke_token(refresh_token)
            
            return {
                "access_token": new_access_token,
                "refresh_token": new_refresh_token,
                "token_type": "bearer"
            }
            
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token"
            )
    
    def logout(self, token: str) -> Dict[str, str]:
        """Revoke a token (add to blacklist)."""
        try:
            # Verify the token is valid before revoking
            payload = verify_token(token)
            revoke_token(token)
            return {"message": "Successfully logged out"}
        except JWTError:
            # Even if token is invalid, return success to prevent token enumeration
            return {"message": "Successfully logged out"}
    
    def get_current_user(self, token: str = Depends(JWTBearer())) -> Dict[str, Any]:
        """Get the current authenticated user from the JWT token."""
        try:
            payload = verify_token(token, TokenType.ACCESS)
            email = payload.get("sub")
            
            if not email:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication credentials"
                )
                
            user_data = self.get_user_by_email(email)
            if not user_data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
                
            # Remove sensitive data
            user_data.pop("password", None)
            return user_data
            
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
