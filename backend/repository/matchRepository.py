import json
import logging
from datetime import datetime
from typing import List, Dict, Optional

from backend.core.database import (
    execute_query, 
    execute_with_commit, 
    cache_get, 
    cache_set, 
    cache_delete,
    generate_cache_key
)

logger = logging.getLogger(__name__)

class MatchRepository:
    """Repository for match results with caching"""
    
    CACHE_PREFIX = "match"
    CACHE_EXPIRY = 43200  # 12 hours
    
    @classmethod
    async def save_match_result(cls, match_data: Dict) -> bool:
        """Save match result to database and cache"""
        try:
            query = """
            INSERT INTO match_results 
                (resume_id, job_id, match_score, matched_skills, missing_skills, 
                required_experience_years, resume_experience_years, created_at)
            VALUES 
                (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (resume_id, job_id) 
            DO UPDATE SET
                match_score = EXCLUDED.match_score,
                matched_skills = EXCLUDED.matched_skills,
                missing_skills = EXCLUDED.missing_skills,
                required_experience_years = EXCLUDED.required_experience_years,
                resume_experience_years = EXCLUDED.resume_experience_years,
                created_at = EXCLUDED.created_at
            """
            
            params = (
                match_data['resume_id'],
                match_data['job_id'],
                match_data['match_score'],
                json.dumps(match_data['matched_skills']),
                json.dumps(match_data['missing_skills']),
                match_data['required_experience_years'],
                match_data['resume_experience_years'],
                datetime.now()
            )
            
            success = await execute_with_commit(query, params)
            
            if success:
                # Update cache
                cache_key = generate_cache_key(cls.CACHE_PREFIX, f"{match_data['resume_id']}:{match_data['job_id']}")
                await cache_set(cache_key, match_data, cls.CACHE_EXPIRY)
            
            return success
            
        except Exception as e:
            logger.error(f"Error saving match result: {str(e)}")
            return False
    
    @classmethod
    async def get_job_and_matches_by_resume_id(cls, resume_id: str, limit: int = 20, min_score: float = 50.0) -> List[Dict]:
        """Get all match results for a resume, ordered by match score"""
        try:
            query = """
            SELECT m.*, j.title, j.company, j.location, j.apply_url
            FROM match_results m
            JOIN jobs j ON m.job_id = j.job_id
            WHERE m.resume_id = %s AND m.match_score >= %s
            ORDER BY m.match_score DESC
            LIMIT %s
            """
            
            results = await execute_query(query, (resume_id, min_score, limit))
            
            matches = []
            for row in results:
                match_data = dict(row)
                
                # Parse JSON fields
                if match_data.get('missing_skills') and isinstance(match_data['missing_skills'], str):
                    match_data['missing_skills'] = json.loads(match_data['missing_skills'])
                if match_data.get('matched_skills') and isinstance(match_data['matched_skills'], str):
                    match_data['matched_skills'] = json.loads(match_data['matched_skills'])
                
                matches.append(match_data)
            
            return matches
            
        except Exception as e:
            logger.error(f"Error getting matches for resume: {str(e)}")
            return []
    
    @classmethod
    def get_match_details_by_resume_id(cls, resume_id, job_id):
        """
        Get match result details by resume_id and job_id, with caching.
        
        Args:
            resume_id: The resume identifier
            job_id: The job identifier
            
        Returns:
            dict: Match result data or None if not found
        """
        try:
            # Check cache first
            cache_key = generate_cache_key(cls.CACHE_PREFIX, f"{resume_id}:{job_id}")
            cached_data = cache_get(cache_key)
            
            if cached_data:
                return cached_data
            
            # If not in cache, get from database
            query = "SELECT * FROM match_results WHERE resume_id = %s AND job_id = %s"
            result = execute_query(query, (resume_id, job_id), fetch_one=True)
            
            if result:
                # Process data
                match_data = dict(result)
                
                # Parse JSON fields
                if match_data.get('missing_skills') and isinstance(match_data['missing_skills'], str):
                    match_data['missing_skills'] = json.loads(match_data['missing_skills'])
                if match_data.get('matched_skills') and isinstance(match_data['matched_skills'], str):
                    match_data['matched_skills'] = json.loads(match_data['matched_skills'])
                
                # Update cache
                cache_set(cache_key, match_data, cls.CACHE_EXPIRY)
                
                return match_data
            
            return None
        
        except Exception as e:
            logger.error(f"Error getting match result: {str(e)}")
            return None
    
    @classmethod
    def delete_match_results(cls, resume_id=None, job_id=None):
        """
        Delete match results for a resume, job, or both.
        
        Args:
            resume_id: Optional resume identifier
            job_id: Optional job identifier
            
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        try:
            if resume_id and job_id:
                # Delete specific match
                query = "DELETE FROM match_results WHERE resume_id = %s AND job_id = %s"
                params = (resume_id, job_id)
                
                # Delete from cache
                cache_key = generate_cache_key(cls.CACHE_PREFIX, f"{resume_id}:{job_id}")
                cache_delete(cache_key)
                
            elif resume_id:
                # Delete all matches for a resume
                query = "DELETE FROM match_results WHERE resume_id = %s"
                params = (resume_id,)
                
                # We can't efficiently delete multiple cache keys in this case
                # Redis would need a scan operation which is beyond the scope here
                
            elif job_id:
                # Delete all matches for a job
                query = "DELETE FROM match_results WHERE job_id = %s"
                params = (job_id,)
                
                # We can't efficiently delete multiple cache keys in this case
                
            else:
                # No identifiers provided
                return False
            
            return execute_with_commit(query, params)
        
        except Exception as e:
            logger.error(f"Error deleting match results: {str(e)}")
            return False