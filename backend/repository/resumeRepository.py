import json
import logging
from datetime import datetime
from typing import Optional, Dict

from backend.core.database import (
    execute_query, 
    execute_with_commit, 
    cache_get, 
    cache_set, 
    cache_delete,
    generate_cache_key,
)

logger = logging.getLogger(__name__)

class ResumeRepository:
    """Repository for resume data operations with caching"""
    
    CACHE_PREFIX = "resume"
    CACHE_EXPIRY = 86400  # 24 hours
    
    @classmethod
    async def save_resume(cls, resume_data: Dict) -> bool:
        """
        Save resume data to database and cache.
        
        Args:
            resume_data: Dictionary containing resume information
                - resume_id: Unique identifier for the resume
                - user_id: User identifier
                - raw_text: Raw text of the resume
                - features: Dictionary containing features of the resume
        
        Returns:
            bool: True if save was successful, False otherwise
        """
        try:
            # Insert or update in database
            query = """
            INSERT INTO user_resumes 
                (resume_id, user_id, features, raw_text, created_at) 
            VALUES 
                (%s, %s, %s, %s, %s)
            ON CONFLICT (resume_id) 
            DO UPDATE SET
                features = EXCLUDED.features,
                raw_text = EXCLUDED.raw_text
            """
            
            values = (
                resume_data['resume_id'],
                resume_data['user_id'],
                json.dumps(resume_data['features']),
                resume_data.get('raw_text', ''),
                datetime.now()
            )
            
            result = await execute_with_commit(query, values)
            
            if result:
                # Update cache with resume_id, user_id, raw_text, processed_date, features for the resume to be used by the matching service
                cache_key = generate_cache_key(cls.CACHE_PREFIX, resume_data['resume_id'])
                cache_set(cache_key, resume_data['features'], cls.CACHE_EXPIRY)
            
            return result is not None
        
        except Exception as e:
            logger.error(f"Error saving resume: {str(e)}")
            return False
    
    @classmethod
    async def get_resume_by_userid(cls, user_id: str) -> Optional[Dict]:
        """Get resume by user ID from database"""
        try:
            query = """
                SELECT * FROM user_resumes WHERE user_id = $1
            """
            result = execute_query(query, (user_id,), fetch_one=True)
            if result:
                return dict(result)
            return None
        except Exception as e:
            logger.error(f"Error getting resume by user ID: {e}")
            return None
    
    @classmethod
    def get_resume_by_id(cls, resume_id):
        """
        Get resume data by ID, with caching.
        
        Args:
            resume_id: The unique identifier of the resume
            
        Returns:
            dict: Resume data or None if not found
        """
        try:
            # Check cache first
            cache_key = generate_cache_key(cls.CACHE_PREFIX, resume_id)
            cached_data = cache_get(cache_key)
            
            if cached_data:
                return cached_data
            
            # If not in cache, get from database
            query = "SELECT * FROM user_resumes WHERE resume_id = %s"
            result = execute_query(query, (resume_id,), fetch_one=True)
            
            if result:
                # Convert database row to dictionary
                resume_dict = dict(result)
                
                # Parse JSON fields if they exist
                for field in ['features', 'raw_text', 'created_at']:
                    if resume_dict.get(field) and isinstance(resume_dict[field], str):
                        try:
                            resume_dict[field] = json.loads(resume_dict[field])
                        except json.JSONDecodeError:
                            pass  # Keep as string if not valid JSON
                
                return resume_dict
            
            return None
        
        except Exception as e:
            logger.error(f"Error getting resume by ID: {str(e)}")
            return None
    
    @classmethod
    def get_resumes_by_user(cls, user_id):
        """
        Get all resumes for a user.
        
        Args:
            user_id: The user identifier
            
        Returns:
            list: List of resume data dictionaries
        """
        try:
            query = "SELECT * FROM user_resumes WHERE user_id = %s ORDER BY created_at DESC"
            results = execute_query(query, (user_id,))
            
            resumes = []
            for row in results:
                resume_data = dict(row)
                
                # Parse JSON fields
                for field in ['features', 'raw_text', 'created_at', 'processed_date']:
                    if resume_data.get(field) and isinstance(resume_data[field], str):
                        resume_data[field] = json.loads(resume_data[field])
                
                resumes.append(resume_data)
            
            return resumes
        
        except Exception as e:
            logger.error(f"Error getting resumes by user: {str(e)}")
            return []
    
    @classmethod
    def delete_resume(cls, resume_id):
        """
        Delete a resume by ID.
        
        Args:
            resume_id: The unique identifier of the resume
            
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        try:
            # Delete from database
            query = "DELETE FROM user_resumes WHERE resume_id = %s"
            success = execute_with_commit(query, (resume_id,))
            
            if success:
                # Delete from cache
                cache_key = generate_cache_key(cls.CACHE_PREFIX, resume_id)
                cache_delete(cache_key)
            
            return success
        
        except Exception as e:
            logger.error(f"Error deleting resume: {str(e)}")
            return False
