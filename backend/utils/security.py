# backend/utils/security.py
from passlib.context import CryptContext
from datetime import datetime, timedelta
import os
from typing import Optional, Dict, Any
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from backend.api.models.user import User
from backend.repository.userRepositoty import UserRepository
from datetime import timezone

# Initialize password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = os.getenv("SECRET_KEY") # should be a random string
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# OAuth2 scheme for token extraction
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password for storage"""
    return pwd_context.hash(password)

# User logs in → receives both access and refresh tokens
# Access token expires after 30 minutes
# User uses refresh token to get a new access token without re-logging in
# This continues until the refresh token expires (7 days)
# Then user must log in again with credentials
def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token from a dictionary of data"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, "token_type": "access"})
    # Creates the actual JWT token using:
    # - the data dictionary
    # - a secret key (for signing)
    # - the specified algorithm (HS256)
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: Dict[str, Any]) -> str:
    """Create a JWT refresh token with longer expiry"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "token_type": "refresh"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: str = Depends(oauth2_scheme), user_repo: UserRepository = Depends()) -> User:
    """Decode JWT token and return current user"""
    # when a protected endpoint is accessed, the token is extracted from the request header
    # and passed to this function to check if it's valid
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        token_type = payload.get("token_type")
        
        if user_id is None or token_type != "access":
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
        
    # Get user from database
    user = await user_repo.get_user_by_id(user_id)
    if user is None:
        raise credentials_exception
        
    # Check if user is active
    if not user["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
        
    return User(**user)

# Optional dependency for admin-only endpoints
async def get_current_active_admin(current_user: User = Depends(get_current_user)) -> User:
    """Check if current user is an admin"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user