from backend.api.models.user import UserInDB
from datetime import datetime
from typing import Optional, Dict, Any
from backend.core.database import (
    execute_query, 
    execute_with_commit, 
)
class UserRepository:
    async def create_user(self, user: UserInDB) -> str:
        query = """
        INSERT INTO users (user_id, email, full_name, hashed_password, is_active, is_verified, role, created_at, updated_at)
        VALUES (%(user_id)s, %(email)s, %(full_name)s, %(hashed_password)s, %(is_active)s, %(is_verified)s, %(role)s, %(created_at)s, %(updated_at)s)
        RETURNING user_id
        """
    
        params = {
            "user_id": user.user_id,
            "email": user.email,
            "full_name": user.full_name,
            "hashed_password": user.hashed_password,
            "is_active": user.is_active,
            "is_verified": user.is_verified,
            "role": user.role,
            "created_at": user.created_at,
            "updated_at": user.updated_at
        }
        result = await execute_query(query, params, fetch_one=True)
        print("result", result)
        return result['user_id'] if result else None
    
    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        query = "SELECT * FROM users WHERE email = %s"
        return await execute_query(query, (email,), fetch_one=True)
    
    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        query = "SELECT * FROM users WHERE user_id = %s"
        return await execute_query(query, (user_id,), fetch_one=True)
    
    async def update_user(self, user_id: str, update_data: Dict[str, Any]) -> bool:
        """Update user fields"""
        # Build dynamic update query based on provided fields
        update_parts = []
        params = []
        
        for key, value in update_data.items():
            update_parts.append(f"{key} = %s")
            params.append(value)
            
        # Add updated_at timestamp
        update_parts.append("updated_at = %s")
        params.append(datetime.now())
        
        # Add user_id for WHERE clause
        params.append(user_id)
        
        query = f"""
        UPDATE users 
        SET {", ".join(update_parts)}
        WHERE user_id = %s
        """
        
        print(query)
        
        return await execute_with_commit(query, params)

    async def verify_user(self, user_id: str) -> bool:
        """Mark a user as verified"""
        query = """
        UPDATE users
        SET is_verified = TRUE, updated_at = %s
        WHERE user_id = %s
        """
        return await execute_with_commit(query, (datetime.now(), user_id))
    
    async def delete_user(self, user_id: str) -> bool:
        """Delete a user"""
        query = "DELETE FROM users WHERE user_id = %s"
        return await execute_with_commit(query, (user_id,))