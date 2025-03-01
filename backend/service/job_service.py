import os
from typing import List, Dict, Any
from datetime import datetime
from fastapi import HTTPException
from redis import Redis
from linkedin_api import Linkedin
from dotenv import load_dotenv
from backend.service.feature_service import FeatureService
from backend.service.redis_service import RedisClient
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import pandas as pd
import time
from backend.utils.file_processors import ExcelFileHandler
import asyncio
import json  # Add this import at the top

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
    def __init__(self, feature_service: FeatureService, redis_client: Redis):
        self.feature_service = feature_service
        self.redis_client = redis_client
        self.executor = ThreadPoolExecutor(max_workers=MAX_SEARCH_WORKERS)
        try:
            self.linkedin_api = Linkedin(LINKEDIN_USERNAME, LINKEDIN_PASSWORD)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to initialize LinkedIn API: {str(e)}"
            )

    async def search_jobs(self, search_params: Dict) -> List[Dict]:
        """Search for jobs with given parameters"""
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
                    if job['job_id'] not in seen_jobs:
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
        return self.redis_client.exists(self._get_cache_key(job_id))

    async def cache_job(self, job_id: str, job_details: Dict):
        """Cache job details"""
        try:
            # Serialize the dictionary to JSON string
            serialized_data = json.dumps(job_details)
            
            self.redis_client.set(
                name=self._get_cache_key(job_id),
                value=serialized_data,
                ex=JOB_CACHE_EXPIRY
            )
        except Exception as e:
            print(f"Error caching job {job_id}: {e}")

    def get_cached_job(self, job_id: str) -> Dict:
        """Get cached job details"""
        try:
            cached_data = self.redis_client.get(self._get_cache_key(job_id))
            if cached_data:
                # Deserialize JSON string back to dictionary
                return json.loads(cached_data)
            return None
        except Exception as e:
            print(f"Error retrieving cached job {job_id}: {e}")
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
            return datetime.fromtimestamp(int(listed_time)/1000).strftime('%Y-%m-%d %H:%M')
        return listed_time

    def get_apply_url(self, details: Dict) -> str:
        """Extract apply URL from job details"""
        apply_method = (details.get('applyMethod', {})
            .get('com.linkedin.voyager.jobs.OffsiteApply', {}) or 
            details.get('applyMethod', {})
            .get('com.linkedin.voyager.jobs.ComplexOnsiteApply', {}))
        return apply_method.get('companyApplyUrl', 'N/A')

    async def process_job(self, job: Dict) -> Dict:
        """Process a single job posting"""
        try:
            job_id = job["entityUrn"].split(":")[-1]
            
            # Check cache first
            if self.is_job_processed(job_id):
                cached_job = self.get_cached_job(job_id)
                if cached_job:
                    return cached_job
            
            # Get full job details
            details = self.linkedin_api.get_job(job_id)
            
            # Extract metadata
            metadata = self.extract_metadata(details)
            
            # Skip blacklisted companies
            if metadata['company'] in BLACK_LIST:
                return None
            
            # Get job description and process it
            job_desc = details.get('description', {}).get('text', '')
            job_features = self.feature_service.extract_job_features(job_desc)
            
            # Prepare final result
            job_result = {
                "job_id": job_id,
                "title": metadata['title'],
                "company": metadata['company'],
                "location": metadata['location'],
                "workplace_type": metadata['workplace_type'],
                "listed_date": metadata['listed_time'],
                "apply_url": self.get_apply_url(details),
                "description": job_desc,
                "features": job_features,
                "processed_date": datetime.now().isoformat()
            }
            
            # Cache the result
            await self.cache_job(job_id, job_result)
            
            return job_result
            
        except Exception as e:
            print(f"Error processing job: {e}")
            return None

    def process_jobs_in_batch(self, jobs, batch_size=45):
        """Process jobs in batches to better manage resources"""
        with ThreadPoolExecutor(max_workers=MAX_PROCESS_WORKERS) as executor:
            futures = []
            for i in range(0, len(jobs), batch_size):
                batch = jobs[i:i+batch_size]
                futures.extend([executor.submit(self.process_job, job) for job in batch])
                
            result = []
            for future in futures:
                try:
                    job_result = future.result()
                    if job_result is not None:
                        result.append(job_result)
                except Exception as e:
                    print(f"Error processing job: {e}")
                    
        return result
    
    async def get_job_by_id(self, job_id: str) -> Dict:
        """Get job details by ID"""
        try:
            # Check cache first
            cached_job = self.get_cached_job(job_id)
            if cached_job:
                return cached_job
            
            # Get from LinkedIn API
            job_details = self.linkedin_api.get_job(job_id)
            if not job_details:
                raise HTTPException(
                    status_code=404,
                    detail=f"Job not found: {job_id}"
                )
            
            # Process and cache the job
            job_result = await self.process_job({"entityUrn": f"urn:li:fs_normalized_jobPosting:{job_id}"})
            return job_result
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error getting job details: {str(e)}"
            )

# Example usage
async def main():
    from redis import Redis
    from datetime import datetime, timedelta
    
    # Initialize services
    redis_client = Redis(host='localhost', port=6379, db=0)
    feature_service = FeatureService()
    job_service = JobService(feature_service, redis_client)
    
    # Search parameters
    search_params_list = [
        {
            "keywords": "Software Engineer",
            "location_name": "United States",
            "remote": ["2"],
            "experience": ["2", "3"],
            "job_type": ["F", "C"],
            "limit": 3,
        },
        {
            "keywords": "Software Developer",
            "location_name": "United States",
            "experience": ["2", "3"],
            "job_type": ["F", "C"],
            "limit": 1,
        },
        {
            "keywords": "Backend",
            "location_name": "United States",
            "experience": ["2", "3"],
            "job_type": ["F", "C"],
            "limit": 1,
        }
    ]
    
    print(f"Starting job search at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run parallel search
    jobs = await job_service.search_jobs_parallel(search_params_list)
    
    print(f"Found {len(jobs)} unique jobs")
    for job in jobs:
        print(f"- {job['title']} at {job['company']}")

if __name__ == "__main__":
    asyncio.run(main())
