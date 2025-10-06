import json
import uuid
from pathlib import Path
from typing import Optional, Dict, Any
from pydantic import EmailStr
from fastapi import HTTPException, status
from ..models.user import UserCreate, User
from ..auth import get_password_hash, verify_password

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

    def create_user(self, user: UserCreate) -> User:
        users = self._load_users()
        
        # Check if user already exists
        if any(u["email"] == str(user.email) for u in users):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Hash the password
        hashed_password = get_password_hash(user.password)

        # Create new user with UUID
        new_user = {
            "id": str(uuid.uuid4()),
            "email": str(user.email),
            "username": user.username,
            "password": hashed_password
        }
        
        users.append(new_user)
        self._save_users(users)
        
        # Return Pydantic User model
        return User(**new_user)

    def get_user_by_email(self, email: EmailStr) -> Optional[Dict[str, Any]]:
        users = self._load_users()
        for user in users:
            if user["email"] == str(email):
                return user # Return full user data including password hash for internal use
        return None

    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        print(f"Attempting to authenticate user with email: '{email}'")
        
        # Normalize email for comparison
        normalized_email = email.lower().strip()
        
        user_data = self.get_user_by_email(EmailStr(normalized_email))
        
        if user_data:
            if verify_password(password, user_data.get("password")):
                print(f"User '{email}' authenticated successfully.")
                return User(**user_data)
            else:
                print(f"Password mismatch for user '{email}'.")
        
        print(f"Authentication failed for email: '{email}'")
        return None # Return None instead of raising HTTPException here

    def update_user_password(self, email: EmailStr, new_password: str) -> User:
        users = self._load_users()
        updated = False
        for i, user in enumerate(users):
            if user["email"] == str(email):
                users[i]["password"] = get_password_hash(new_password)
                updated = True
                break
        
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        self._save_users(users)
        # Return the updated user, excluding the password hash
        updated_user_data = self.get_user_by_email(email)
        return User(**updated_user_data)
