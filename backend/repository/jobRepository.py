import json
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, List

from backend.core.database import (
    execute_query, 
    execute_with_commit, 
    cache_get, 
    cache_set, 
    cache_delete,
    generate_cache_key
)

logger = logging.getLogger(__name__)

class JobRepository:
    """Repository for job data operations with caching"""
    
    CACHE_PREFIX = "job"
    CACHE_EXPIRY = 86400  # 24 hours (jobs are less frequently updated)
    
    @classmethod
    async def save_job(cls, job_data: Dict) -> bool:
        """
        Save job data to database and cache.
        
        Args:
            job_data: Dictionary containing job information
                - job_id: Unique identifier for the job
                - title: Job title
                - company: Company name
                - location: Job location
                - description: Job description
                - features: Job features including skills, experience requirements
                - apply_url: URL to apply
                - listed_date: When the job was listed
                
        Returns:
            bool: True if save was successful, False otherwise
        """
        try:
            # Insert or update in database
            query = """
            INSERT INTO jobs 
                (job_id, title, company, location, workplace_type, listed_date, apply_url, description, features, processed_date,
                created_at) 
            VALUES 
                (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (job_id) 
            DO UPDATE SET
                title = EXCLUDED.title,
                company = EXCLUDED.company,
                location = EXCLUDED.location,
                workplace_type = EXCLUDED.workplace_type,
                listed_date = EXCLUDED.listed_date,
                apply_url = EXCLUDED.apply_url,
                description = EXCLUDED.description,
                features = EXCLUDED.features,
                processed_date = EXCLUDED.processed_date
            """

            now = datetime.now()
            
            params = (
                job_data['job_id'],
                job_data['title'],
                job_data['company'],
                job_data['location'],
                job_data.get('workplace_type', 'N/A'),
                job_data.get('listed_date', 'N/A'),
                job_data.get('apply_url', 'N/A'),
                job_data.get('description', ''),
                json.dumps(job_data.get('features', {})),
                job_data.get('processed_date', now.isoformat()),
                now
            )
            
            success = await execute_with_commit(query, params)
            
            if success:
                # Update cache
                cache_key = generate_cache_key(cls.CACHE_PREFIX, job_data['job_id'])
                await cache_set(cache_key, job_data, cls.CACHE_EXPIRY)
            
            return success
        
        except Exception as e:
            logger.error(f"Error saving job: {str(e)}")
            return False
    
    @classmethod
    async def get_job_by_id(cls, job_id: str) -> Optional[Dict]:
        """Get job by ID"""
        try:
            # Try cache first
            cache_key = generate_cache_key(cls.CACHE_PREFIX, job_id)
            cached_job = await cache_get(cache_key)
            if cached_job:
                return cached_job
                
            # If not in cache, get from database
            query = "SELECT * FROM jobs WHERE job_id = %s"
            result = await execute_query(query, (job_id,), fetch_one=True)
            
            if result:
                job_data = dict(result)
                
                # Parse features JSON field if it's a string
                if job_data.get('features') and isinstance(job_data['features'], str):
                    job_data['features'] = json.loads(job_data['features'])
                
                # Update cache
                await cache_set(cache_key, job_data, cls.CACHE_EXPIRY)
                
                return job_data
                
            return None
        except Exception as e:
            logger.error(f"Error getting job by ID: {str(e)}")
            return None
    
    @classmethod
    async def search_jobs(cls, criteria: Dict, limit: int = 20, offset: int = 0) -> List[Dict]:
        """
        Search for jobs with various criteria.
        
        Args:
            criteria: Dictionary containing search criteria
                - keywords: Keywords to search in title and description
                - company: Company name
                - location: Job location
                - skills: List of skills to match
            limit: Maximum number of results to return
            offset: Offset for pagination
            
        Returns:
            list: List of job data dictionaries matching criteria
        """
        try:
            # Build the query dynamically based on criteria
            base_query = "SELECT * FROM jobs WHERE 1=1"
            params = []
            
            if criteria.get('keywords'):
                base_query += """ AND (
                    title ILIKE %s 
                    OR description ILIKE %s
                )"""
                keyword_param = f"%{criteria['keywords']}%"
                params.extend([keyword_param, keyword_param])
            
            if criteria.get('company'):
                base_query += " AND company ILIKE %s"
                params.append(f"%{criteria['company']}%")
            
            if criteria.get('location'):
                base_query += " AND location ILIKE %s"
                params.append(f"%{criteria['location']}%")
            
            if criteria.get('skills') and isinstance(criteria['skills'], list):
                # For PostgreSQL JSONB searching in features->skills
                for skill in criteria['skills']:
                    base_query += " AND features->>'skills' @> %s"
                    params.append(json.dumps([skill]))
            
            # Add sorting and pagination
            base_query += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
            params.extend([limit, offset])
            
            # Execute query
            results = await execute_query(base_query, params)
            
            jobs = []
            for row in results:
                job_data = dict(row)
                
                # Parse features JSON field
                if job_data.get('features') and isinstance(job_data['features'], str):
                    job_data['features'] = json.loads(job_data['features'])
                
                jobs.append(job_data)
            
            return jobs
        
        except Exception as e:
            logger.error(f"Error searching jobs: {str(e)}")
            return []
    
    @classmethod
    async def get_recent_jobs(cls, days: int = 30, limit: int = 50) -> List[Dict]:
        """
        Get recent jobs from the last X days.
        
        Args:
            days: Number of days to look back
            limit: Maximum number of results
            
        Returns:
            list: List of recent job data dictionaries
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            query = """
            SELECT * FROM jobs 
            WHERE created_at >= %s 
            ORDER BY created_at DESC 
            LIMIT %s
            """
            
            results = await execute_query(query, (cutoff_date, limit))
            
            jobs = []
            for row in results:
                job_data = dict(row)
                
                # Parse features JSON field
                if job_data.get('features') and isinstance(job_data['features'], str):
                    job_data['features'] = json.loads(job_data['features'])
                
                jobs.append(job_data)
            
            return jobs
        
        except Exception as e:
            logger.error(f"Error getting recent jobs: {str(e)}")
            return []
    
    @classmethod
    async def is_job_expired(cls, job_id: str, days_threshold: int = 30) -> bool:
        """
        Check if a job needs to be refreshed from the source.
        
        Args:
            job_id: The unique identifier of the job
            days_threshold: Days after which a job is considered expired
            
        Returns:
            bool: True if job is expired, False otherwise
        """
        try:
            query = """
            SELECT updated_at FROM jobs 
            WHERE job_id = %s
            """
            
            result = await execute_query(query, (job_id,), fetch_one=True)
            
            if not result:
                return True  # Job doesn't exist, so it's "expired"
            
            updated_at = result['updated_at']
            expiry_date = datetime.now() - timedelta(days=days_threshold)
            
            return updated_at < expiry_date
        
        except Exception as e:
            logger.error(f"Error checking if job is expired: {str(e)}")
            return True  # Assume expired on error