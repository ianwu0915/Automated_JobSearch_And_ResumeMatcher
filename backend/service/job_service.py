import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from fastapi import HTTPException
from redis import Redis
from linkedin_api import Linkedin
from dotenv import load_dotenv
from backend.service.redis_service import RedisClient
from backend.repository.jobRepository import JobRepository
from backend.utils.feature_extractors import FeatureExtractor
from backend.core.database import initialize_database
from concurrent.futures import ThreadPoolExecutor

import asyncio
import json

# Load environment variables
load_dotenv()

# LinkedIn API Credentials
LINKEDIN_USERNAME = os.getenv('LINKEDIN_USERNAME')
LINKEDIN_PASSWORD = os.getenv('LINKEDIN_PASSWORD')

# Job Cache Settings
JOB_CACHE_EXPIRY = int(os.getenv('JOB_CACHE_EXPIRY', 3600))
JOB_KEY_PREFIX = os.getenv('JOB_KEY_PREFIX', 'job:')

# Search Settings
MAX_SEARCH_WORKERS = int(os.getenv('MAX_SEARCH_WORKERS', 5))
MAX_PROCESS_WORKERS = int(os.getenv('MAX_PROCESS_WORKERS', 20))

# Filtering
BLACK_LIST: List[str] = os.getenv('BLACK_LIST', '[]').strip('[]').split(',')
BLACK_LIST = [company.strip().strip('"\'') for company in BLACK_LIST if company.strip()]

class JobService:
    def __init__(self, redis_client=None):
        self.job_repo = JobRepository()
        self.feature_extractor = FeatureExtractor()
        self.redis_client = redis_client or RedisClient()
        self.executor = ThreadPoolExecutor(max_workers=MAX_SEARCH_WORKERS)
        try:
            self.linkedin_api = Linkedin(LINKEDIN_USERNAME, LINKEDIN_PASSWORD)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to initialize LinkedIn API: {str(e)}"
            )
            
    def extract_job_features(self, text: str) -> Dict[str, Any]:
        """Extract features from job description"""
        try:
            features = self.feature_extractor.extract_job_features(text)
            return {
                "required_experience_years": features["required_experience_years"],
                "skills": features["skills"],
                "word_frequencies": dict(list(features["word_frequencies"].items())[:100])
            }
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error extracting job features: {str(e)}"
            ) 
            
    async def search_jobs(self, search_params: Dict) -> List[Dict]:
        """Search for jobs with given parameters and process them"""
        try:
            # Create a wrapper function to handle keyword arguments
            def search_wrapper():
                return self.linkedin_api.search_jobs(**search_params)
            
            # Run LinkedIn API call in thread pool since it's blocking
            jobs = await asyncio.get_event_loop().run_in_executor(
                self.executor,
                search_wrapper  # Pass the wrapper function without arguments
            )
            
            # Process jobs concurrently
            tasks = [self.process_job(job) for job in jobs]
            processed_jobs = await asyncio.gather(*tasks)
            
            # Filter out None results and return valid jobs
            return [job for job in processed_jobs if job is not None]
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error searching jobs: {str(e)}"
            )

    async def search_jobs_parallel(self, search_params_list: List[Dict]) -> List[Dict]:
        """Search for jobs with multiple parameter sets in parallel"""
        try:
            # Create tasks for each search parameter set
            tasks = [self.search_jobs(params) for params in search_params_list]
            
            # Run all searches concurrently
            results = await asyncio.gather(*tasks)
            
            # Flatten results and remove duplicates based on job_id
            seen_jobs = set()
            unique_jobs = []
            
            for job_list in results:
                for job in job_list:
                    if job and job.get('job_id') and job['job_id'] not in seen_jobs:
                        seen_jobs.add(job['job_id'])
                        unique_jobs.append(job)
            
            return unique_jobs
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error in parallel job search: {str(e)}"
            )

    def _get_cache_key(self, job_id: str) -> str:
        """Generate Redis key with prefix"""
        return f"{JOB_KEY_PREFIX}{job_id}"

    def is_job_processed(self, job_id: str) -> bool:
        """Check if job has been processed and cached"""
        try:
            exists = self.redis_client.exists(self._get_cache_key(job_id))
            return exists
        except Exception as e:
            print(f"Error checking if job is processed: {e}")
            return False

    def cache_job(self, job_id: str, job_details: Dict):
        """Cache job details"""
        try:
            # Only serialize if not already a string
            if isinstance(job_details, dict):
                serialized_data = json.dumps(job_details)
            else:
                serialized_data = job_details
                
            self.redis_client.set(
                self._get_cache_key(job_id),
                serialized_data,
                ex=JOB_CACHE_EXPIRY
            )
        except Exception as e:
            print(f"Error caching job {job_id}: {e}")

    def get_cached_job(self, job_id: str) -> Optional[Dict]:        
        """Get cached job details"""
        try:
            cached_data = self.redis_client.get(self._get_cache_key(job_id))
            if cached_data:
                if isinstance(cached_data, bytes):
                    # If it's bytes, decode and parse JSON
                    return json.loads(cached_data.decode('utf-8'))
                elif isinstance(cached_data, str):
                    # If it's string, parse JSON
                    return json.loads(cached_data)
                elif isinstance(cached_data, dict):
                    # If it's already a dict, return as is
                    return cached_data
            return None
        except Exception as e:
            print(f"Error retrieving cached job {job_id}: {e}")
            return None

    def get_job_details_by_id(self, job_id: str) -> Dict:
        """Get detailed job information from LinkedIn API"""
        try:
            return self.linkedin_api.get_job(job_id)
        except Exception as e:
            print(f"Error getting job details from LinkedIn: {e}")
            return None

    def extract_metadata(self, details: Dict) -> Dict:
        """Extract basic metadata from job details"""
        return {
            'title': details.get('title', 'N/A'),
            'company': details.get('companyDetails', {})
                .get('com.linkedin.voyager.deco.jobs.web.shared.WebCompactJobPostingCompany', {})
                .get('companyResolutionResult', {})
                .get('name', 'N/A'),
            'company_url': details.get('companyDetails', {})
                .get('com.linkedin.voyager.deco.jobs.web.shared.WebCompactJobPostingCompany', {})
                .get('companyResolutionResult', {})
                .get('url', 'N/A'),
            'location': details.get('formattedLocation', 'N/A'),
            'workplace_type': details.get('workplaceTypesResolutionResults', {})
                .get('urn:li:fs_workplaceType:2', {})
                .get('localizedName', 'N/A'),
            'listed_time': self.format_listed_time(details.get('listedAt', 'N/A'))
        }

    def format_listed_time(self, listed_time: str) -> str:
        """Convert Unix timestamp to readable date"""
        if listed_time != 'N/A':
            try:
                return datetime.fromtimestamp(int(listed_time)/1000).strftime('%Y-%m-%d %H:%M')
            except (ValueError, TypeError):
                return 'N/A'
        return listed_time

    def get_apply_url(self, details: Dict) -> str:
        """Extract apply URL from job details"""
        apply_method = (details.get('applyMethod', {})
            .get('com.linkedin.voyager.jobs.OffsiteApply', {}) or 
            details.get('applyMethod', {})
            .get('com.linkedin.voyager.jobs.ComplexOnsiteApply', {}))
        return apply_method.get('companyApplyUrl', 'N/A')

    async def process_job(self, job: Dict) -> Optional[Dict]:
        """Process a single job posting"""
        try:
            # Safely extract job_id
            if not job.get("entityUrn"):
                return None
                
            job_id = job["entityUrn"].split(":")[-1]
            
            # Check cache first
            if self.is_job_processed(job_id):
                cached_job = self.get_cached_job(job_id)
                if cached_job:
                    return cached_job
            
            # Check database
            db_job = await self.job_repo.get_job_by_id(job_id)
            if db_job:
                return db_job
            
            # Get full job details
            details = self.get_job_details_by_id(job_id)
            if not details:
                return None
            
            # Extract metadata
            metadata = self.extract_metadata(details)
            
            # Skip blacklisted companies
            if metadata['company'] in BLACK_LIST:
                return None
            
            # Get job description and process it
            job_desc = details.get('description', {}).get('text', '')
            job_features = self.extract_job_features(job_desc)
            
            # Prepare final result
            job_result = {
                "job_id": job_id,
                "title": metadata['title'],
                "company": metadata['company'],
                "location": metadata['location'],
                "workplace_type": metadata['workplace_type'],
                "listed_time": metadata['listed_time'],
                "apply_url": self.get_apply_url(details),
                "description": job_desc,
                "features": job_features,
                "processed_date": datetime.now().isoformat()
            }
            
            # Cache the result
            self.cache_job(job_id, job_result)
            
            # Save to database
            await self.job_repo.save_job(job_result)
            
            return job_result
            
        except Exception as e:
            print(f"Error processing job: {e}")
            return None 

    async def get_job_by_id(self, job_id: str) -> Dict:
        """Get job details by ID"""
        print(f"Getting job by ID: {job_id}")
        try:
            # Check cache first
            # cached_job = await self.get_cached_job(job_id)
            # if cached_job:
            #     print(f"Returning cached job: {cached_job}")
            #     return cached_job
            
            # Check database 
            db_job = await self.job_repo.get_job_by_id(job_id)
            if db_job:
                print(f"Returning database job: {db_job}")
                return db_job
                
            # If not found, fetch from LinkedIn API
            details = self.linkedin_api.get_job(job_id)
            if not details:
                raise HTTPException(
                    status_code=404,
                    detail=f"Job not found: {job_id}"
                )
                
            # Process and return the job
            job_result = await self.process_job({"entityUrn": f"urn:li:fs_normalized_jobPosting:{job_id}"})
            if not job_result:
                raise HTTPException(
                    status_code=404,
                    detail=f"Failed to process job: {job_id}"
                )
                
            return job_result
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error getting job details: {str(e)}"
            )
    
    async def save_job(self, job_data: dict) -> str:
        """Save job to database"""
        try:
            success = await self.job_repo.save_job(job_data)
            if not success:
                raise Exception(f"Failed to save job {job_data.get('job_id')}")
            return job_data["job_id"]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error saving job: {str(e)}")

# Example usage
async def main():
    initialize_database()
    job_service = JobService()
    search_params_list = [
        {
            "keywords": "Software Engineer",
            "location_name": "United States",
            "remote": ["2"],
            "experience": ["2", "3"],
            "job_type": ["F", "C"],
            "limit": 10,
        },
        {
            "keywords": "Software Developer",
            "location_name": "United States",
            "experience": ["2", "3"],
            "job_type": ["F", "C"],
            "limit": 10,
        },
        {
            "keywords": "Backend",
            "location_name": "United States",
            "experience": ["2", "3"],
            "job_type": ["F", "C"],
            "limit": 10,
        }
    ]
    
    jobs = await job_service.search_jobs_parallel(search_params_list)
  
    
    for job in jobs:
        success = await job_service.save_job(job)
        if success:
            print(f"Job saved: {success}")
        else:
            print(f"Failed to save job: {success}")
    
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
