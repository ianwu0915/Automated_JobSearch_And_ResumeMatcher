# backend/routes/auth.py
from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordRequestForm
from typing import Any, Dict

from backend.api.models.user import UserCreate, User
from backend.service.auth_service import AuthService
from backend.repository.userRepositoty import UserRepository
from backend.utils.security import get_current_user

auth_router = APIRouter(prefix="/api/auth", tags=["authentication"])

@auth_router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,  
    user_repo: UserRepository = Depends(),
) -> Dict[str, Any]:
    """Register a new user"""
    auth_service = AuthService(user_repo)
    user_id = await auth_service.register_user(user_data)
    
    return {
        "message": "User registered successfully",
        "user_id": user_id
    }

@auth_router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_repo: UserRepository = Depends(),
) -> Dict[str, Any]:
    """Login for access token"""
    auth_service = AuthService(user_repo)
    tokens = await auth_service.login(form_data.username, form_data.password)
    
    return tokens

@auth_router.post("/refresh")
async def refresh_token(
    refresh_token: str = Body(..., embed=True),
    user_repo: UserRepository = Depends(),
) -> Dict[str, Any]:
    """Get a new access token using refresh token"""
    auth_service = AuthService(user_repo)
    tokens = await auth_service.refresh_token(refresh_token)
    
    return tokens

@auth_router.get("/me", response_model=User)
async def get_me(current_user: User = Depends(get_current_user)) -> User:
    """Get current logged-in user details"""
    return current_user