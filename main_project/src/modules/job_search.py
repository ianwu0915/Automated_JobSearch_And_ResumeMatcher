# Standard library imports
import os
import sys
from pathlib import Path
from redis import RedisClient

# Add src directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(src_dir)

# Import lazy loader
from utils.lazy_module import LazyModule

# Lazy imports
json = LazyModule('json')
time = LazyModule('time')
from datetime import datetime
ThreadPoolExecutor = LazyModule('concurrent.futures').ThreadPoolExecutor

# Third-party lazy imports
pd = LazyModule('pandas')
openai = LazyModule('openai')
load_dotenv = LazyModule('dotenv').load_dotenv
Linkedin = LazyModule('linkedin_api').Linkedin

# Local application lazy imports
process_job_description = LazyModule('job_data_extraction').process_job_description
FileHandler = LazyModule('utils.file_operations').FileHandler

# Load environment variables
load_dotenv()

### Global configurations
BLACK_LIST = ["Revature", "BeaconFire Inc.", "BeaconFire Solution Inc.", "Canonical", "SynergisticIT", "Talentify.io", "Jobs via Dice", "Robert Half"]
MAX_SEARCH_WORKERS = 3  # For parallel job searching
MAX_PROCESS_WORKERS = 20  # For parallel job processing
JOB_CACHE_EXPIRY = 60 * 60 * 24  # 24 hours in seconds
JOB_KEY_PREFIX = "job:"

### Job Search Class
class JobSearch:
    # Initialize the job search class
    def __init__(self):
        self.usrname = os.getenv("LINKEDIN_USERNAME")
        self.pwd = os.getenv("LINKEDIN_PASSWORD")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.api = Linkedin(self.usrname, self.pwd)
        self.redis_client = RedisClient()
        openai.api_key = self.openai_api_key

    def is_job_processed(self, job_id):
        return self.redis_client.exists(self._get_cache_key(job_id))
    
    def mark_job_as_processed(self, job_id, job_details):
        try: 
            self.redis_client.set(
                name=self._get_cache_key(job_id),
                value=job_details,
                ex=JOB_CACHE_EXPIRY
            )
        except Exception as e:
            print(f"Error caching job {job_id}: {e}")
        
        
    def _get_cache_key(self, job_id):
        """Generate Redis key with prefix"""
        return f"{JOB_KEY_PREFIX}{job_id}" # job:1234567890

    def search_jobs(self, search_param):
        # Search for jobs on LinkedIn
        try:
            return self.api.search_jobs(**search_param)
        except Exception as e:
            print(f"Error searching for jobs: {e}")
            return []
    
    def get_job_details_by_id(self, job_id):
        # Get job details by job ID
        try:
            return self.api.get_job(job_id)
        except Exception as e:
            print(f"Error getting job details: {e}")
            return {}

    def match_resume_with_job(self, job_desc, resume_text):
        # Uses OpenAI to calculate match percentage between job description and resume
        try:
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages = [
                    {"role": "system", "content": "You are a job matching AI. Your task is to analyze the similarity between a job description and a resume. Respond with a single integer between 0 and 100, representing the match percentage. Do not include a % symbol, explanation, or any other text."},
                    {"role": "user", "content": f"Evaluate the match percentage between this job description and resume:\n\nJob Description:\n{job_desc}\n\nResume:\n{resume_text}\n\nReturn only a number from 0 to 100."}
                ]
            )
            output = response.choices[0].message.content.strip()
            return int(output) if output.isdigit() else "Unknown"
        except Exception as e:
            print(f"Error calculating match percentage: {e}")
            return "Error"
    
    def filter_job_by_date(self, jobs, days=1):
        # Filter jobs by date posted (within the last 'days' days)
        current_time = datetime.now()
        filtered_jobs = []
        for job in jobs:
            listed_time = job.get('listedAt', 'N/A')
            if listed_time != 'N/A':
                listed_time = datetime.fromtimestamp(int(listed_time)/1000)
                if (current_time - listed_time).days <= days:
                    filtered_jobs.append(job)
        return filtered_jobs

    def search_jobs_parallel(self, search_params_list, max_workers=MAX_SEARCH_WORKERS):
        # Search for jobs on LinkedIn using multiple threads
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            results = list(executor.map(self.search_jobs, search_params_list))
        return [job for sublist in results if sublist for job in sublist]

    def search_jobs_sequential(self, search_params_list):
        # Search for jobs on LinkedIn sequentially (single thread)
        results = []
        for params in search_params_list:
            jobs = self.search_jobs(params)
            if jobs:
                results.extend(jobs)
        return results
    
    def extract_metadata(self, details):
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
            'listed_time': details.get('listedAt', 'N/A')
        }

    def format_listed_time(self, listed_time):
        """Convert Unix timestamp to readable date"""
        if listed_time != 'N/A':
            return datetime.fromtimestamp(int(listed_time)/1000).strftime('%Y-%m-%d %H:%M')
        return listed_time

    def get_apply_url(self, details):
        """Extract apply URL from job details"""
        apply_method = (details.get('applyMethod', {})
            .get('com.linkedin.voyager.jobs.OffsiteApply', {}) or 
            details.get('applyMethod', {})
            .get('com.linkedin.voyager.jobs.ComplexOnsiteApply', {}))
        return apply_method.get('companyApplyUrl', 'N/A')

    def process_job(self, job):
        """Process a single job"""
        try:
            # Get job details
            job_id = job["entityUrn"].split(":")[-1]
            
            if self.is_job_processed(job_id):
                print(f"Job {job_id} already processed. Skipping...")
                return None
            
            details = self.get_job_details_by_id(job_id)
            
            # Extract metadata
            metadata = self.extract_metadata(details)
            
            # Skip blacklisted companies
            if metadata['company'] in BLACK_LIST:
                return None
            
            # Get job description and process it
            job_desc = details.get('description', {}).get('text', '')
            job_data = process_job_description(job_desc)
            
            # Prepare final result
            job_result = {
                "Listed Date": self.format_listed_time(metadata['listed_time']),
                "Job Title": metadata['title'],
                "Company": metadata['company'],
                "Location": metadata['location'],
                "Workplace Type": metadata['workplace_type'],
                "Skills": job_data.get("skills"),
                "Experience Level": job_data.get("experience_level"),
                "Salary": job_data.get("salary"),
                "Apply URL": self.get_apply_url(details)
            }
            
            self.mark_job_as_processed(job_id, job_result)
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
    
        
# Test the job search
def main():
    start_time = time.time()
    print(f"Starting job search at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    search_params_list = [
        {
            "keywords": "Software Engineer",
            "location_name": "United States",
            "remote": ["2"],
            "experience": ["2", "3"],
            "job_type": ["F", "C"],
            "limit": 100,
        },
        {
            "keywords": "Software Developer",
            "location_name": "United States",
            "experience": ["2", "3"],
            "job_type": ["F", "C"],
            "limit": 50,
        },
        {
            "keywords": "Backend",
            "location_name": "United States",
            "experience": ["2", "3"],
            "job_type": ["F", "C"],
            "limit": 50,
        }
    ]
    
    job_search = JobSearch()
    # Uncomment one of these lines to compare:
    # jobs = job_search.search_jobs_sequential(search_params_list)  # Single thread
    jobs = job_search.search_jobs_parallel(search_params_list)      # Multi thread
    
    print(f"\nJob search completed in {time.time() - start_time:.2f} seconds")
    print(f"Found {len(jobs)} jobs")
    
    # Process jobs in parallel
    process_start = time.time()
    with ThreadPoolExecutor(max_workers=MAX_PROCESS_WORKERS) as executor:
        job_results = list(filter(None, executor.map(job_search.process_job, jobs)))
        
    # job_results = job_search.process_jobs_in_batch(jobs)
    print(f"Time taken to process {len(job_results)} jobs: {time.time() - process_start:.2f} seconds")
    
    # Convert to DataFrame and save results
    df = pd.DataFrame(job_results)

    # Create output directory
    output_dir = Path("../output")
    output_dir.mkdir(exist_ok=True)

    # Save data using utility functions
    file_handler = FileHandler()
    json_path = file_handler.save_to_json(job_results, output_dir)
    excel_path = file_handler.save_to_excel(df, output_dir)
    
    print(f"Data saved successfully to:\n- {json_path}\n- {excel_path}")

if __name__ == "__main__":
    main()
