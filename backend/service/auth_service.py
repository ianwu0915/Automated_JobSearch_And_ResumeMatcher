# backend/service/auth_service.py
from typing import Optional, Dict, Any, Tuple
from datetime import timedelta, datetime
from fastapi import HTTPException, status
import uuid
import jwt
import os
from backend.repository.userRepositoty import UserRepository
from backend.api.models.user import UserCreate, UserInDB, User
from backend.utils.security import (
    get_password_hash, 
    verify_password, 
    create_access_token, 
    create_refresh_token
)

SECRET_KEY = os.getenv("SECRET_KEY") # should be a random string
ALGORITHM = "HS256"

class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def register_user(self, user_data: UserCreate) -> str:
        """ Register a new user """
        # Check if user already exists
        existing_user = await self.user_repo.get_user_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        now = datetime.now()
        user_in_db = UserInDB(
            user_id=str(uuid.uuid4()),
            email=user_data.email,
            full_name=user_data.full_name,
            hashed_password=get_password_hash(user_data.password),
            is_active=True,
            is_verified=False,
            role="user",
            created_at=now,
            updated_at=now
        )
        print("user_in_db", user_in_db)
        try: 
            user_id = await self.user_repo.create_user(user_in_db)
            print("user_id", user_id)
            return user_id
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to register user: {str(e)}"
            )
    
    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """ Authenticate a user """
        user = await self.user_repo.get_user_by_email(email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        if not verify_password(password, user["hashed_password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        return User(**user)
    
    async def login(self, email: str, password: str) -> Dict[str, str]:
        """ Login a user and return access and refresh tokens """
        user = await self.authenticate_user(email, password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Inactive user"
            )
        
        # Generate access and refresh tokens
        access_token = create_access_token(
            data={"sub": user.user_id},
            expires_delta=timedelta(minutes=30)
        )
        
        refresh_token = create_refresh_token(
            data={"sub": user.user_id}
        )
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
        
    async def refresh_token(self, refresh_token: str) -> Dict[str, str]:
        """Generate a new access token from a refresh token"""
        try:
            # Decode and validate refresh token (simplified - use a function similar to get_current_user)
            payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id = payload.get("sub")
            token_type = payload.get("token_type")
            
            if not user_id or token_type != "refresh":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid refresh token"
                )
                
            # Check if user exists and is active
            user = await self.user_repo.get_user_by_id(user_id)
            if not user or not user["is_active"]:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found or inactive"
                )
                
            # Generate new access token
            access_token = create_access_token(data={"sub": user_id})
            
            return {
                "access_token": access_token,
                "token_type": "bearer"
            }
            
        except jwt.PyJWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
           
        
        