import json
import logging
from datetime import datetime, timedelta

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
    def save_job(cls, job_data):
        """
        Save job data to database and cache.
        
        Args:
            job_data: Dictionary containing job information
                - job_id: Unique identifier for the job
                - title: Job title
                - company: Company name
                - location: Job location
                - description: Job description
                - required_skills: List of required skills
                - required_experience: Experience requirement
                - required_education: Education requirement
                - word_frequencies: Word frequency dictionary
                - apply_url: URL to apply
                - listed_time: When the job was listed
                
        Returns:
            bool: True if save was successful, False otherwise
        """
        try:
            # Insert or update in database
            query = """
            INSERT INTO jobs 
                (job_id, title, company, location, workplace_type, description, 
                required_skills, required_experience, required_education, 
                word_frequencies, apply_url, listed_time, created_at, updated_at) 
            VALUES 
                (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (job_id) 
            DO UPDATE SET
                title = EXCLUDED.title,
                company = EXCLUDED.company,
                location = EXCLUDED.location,
                workplace_type = EXCLUDED.workplace_type,
                description = EXCLUDED.description,
                required_skills = EXCLUDED.required_skills,
                required_experience = EXCLUDED.required_experience,
                required_education = EXCLUDED.required_education,
                word_frequencies = EXCLUDED.word_frequencies,
                apply_url = EXCLUDED.apply_url,
                listed_time = EXCLUDED.listed_time,
                updated_at = EXCLUDED.updated_at
            """
            
            now = datetime.now()
            
            params = (
                job_data['job_id'],
                job_data['title'],
                job_data['company'],
                job_data.get('location'),
                job_data.get('workplace_type'),
                job_data.get('description', ''),
                json.dumps(job_data.get('required_skills', [])),
                job_data.get('required_experience'),
                json.dumps(job_data.get('required_education', {})),
                json.dumps(job_data.get('word_frequencies', {})),
                job_data.get('apply_url'),
                job_data.get('listed_time'),
                now,
                now
            )
            
            success = execute_with_commit(query, params)
            
            if success:
                # Update cache
                cache_key = generate_cache_key(cls.CACHE_PREFIX, job_data['job_id'])
                cache_set(cache_key, job_data, cls.CACHE_EXPIRY)
            
            return success
        
        except Exception as e:
            logger.error(f"Error saving job: {str(e)}")
            return False
    
    @classmethod
    def get_job_by_id(cls, job_id):
        """
        Get job data by ID, with caching.
        
        Args:
            job_id: The unique identifier of the job
            
        Returns:
            dict: Job data or None if not found
        """
        try:
            # Check cache first
            cache_key = generate_cache_key(cls.CACHE_PREFIX, job_id)
            cached_data = cache_get(cache_key)
            
            if cached_data:
                return cached_data
            
            # If not in cache, get from database
            query = "SELECT * FROM jobs WHERE job_id = %s"
            result = execute_query(query, (job_id,), fetch_one=True)
            
            if result:
                # Process data
                job_data = dict(result)
                
                # Parse JSON fields
                for field in ['required_skills', 'required_education', 'word_frequencies']:
                    if job_data.get(field) and isinstance(job_data[field], str):
                        job_data[field] = json.loads(job_data[field])
                
                # Update cache
                cache_set(cache_key, job_data, cls.CACHE_EXPIRY)
                
                return job_data
            
            return None
        
        except Exception as e:
            logger.error(f"Error getting job by ID: {str(e)}")
            return None
    
    @classmethod
    def search_jobs(cls, criteria, limit=20, offset=0):
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
                # Search for jobs that have any of the specified skills
                placeholders = ', '.join(['%s'] * len(criteria['skills']))
                base_query += f""" AND required_skills ?| array[{placeholders}]"""
                params.extend(criteria['skills'])
            
            # Add sorting and pagination
            base_query += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
            params.extend([limit, offset])
            
            # Execute query
            results = execute_query(base_query, params)
            
            jobs = []
            for row in results:
                job_data = dict(row)
                
                # Parse JSON fields
                for field in ['required_skills', 'required_education', 'word_frequencies']:
                    if job_data.get(field) and isinstance(job_data[field], str):
                        job_data[field] = json.loads(job_data[field])
                
                jobs.append(job_data)
            
            return jobs
        
        except Exception as e:
            logger.error(f"Error searching jobs: {str(e)}")
            return []
    
    @classmethod
    def get_recent_jobs(cls, days=30, limit=50):
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
            
            results = execute_query(query, (cutoff_date, limit))
            
            jobs = []
            for row in results:
                job_data = dict(row)
                
                # Parse JSON fields
                for field in ['required_skills', 'required_education', 'word_frequencies']:
                    if job_data.get(field) and isinstance(job_data[field], str):
                        job_data[field] = json.loads(job_data[field])
                
                jobs.append(job_data)
            
            return jobs
        
        except Exception as e:
            logger.error(f"Error getting recent jobs: {str(e)}")
            return []
    
    @classmethod
    def is_job_expired(cls, job_id, days_threshold=30):
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
            
            result = execute_query(query, (job_id,), fetch_one=True)
            
            if not result:
                return True  # Job doesn't exist, so it's "expired"
            
            updated_at = result['updated_at']
            expiry_date = datetime.now() - timedelta(days=days_threshold)
            
            return updated_at < expiry_date
        
        except Exception as e:
            logger.error(f"Error checking if job is expired: {str(e)}")
            return True  # Assume expired on error
