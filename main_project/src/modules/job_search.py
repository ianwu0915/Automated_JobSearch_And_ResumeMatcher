from linkedin_api import Linkedin
from dotenv import load_dotenv
import os
from pathlib import Path

class JobSearch:
    def __init__(self):
        load_dotenv()
        self.usrname=os.getenv("LINKEDIN_USERNAME")
        self.pwd=os.getenv("LINKEDIN_PASSWORD")
        self.api=Linkedin(self.usrname,self.pwd)

    def search_jobs(self,search_param):
        """Search for jobs on LinkedIn"""
        try:
            jobs=self.api.search_jobs(**search_param)
            return jobs
        except Exception as e:
            print(f"Error searching for jobs: {e}")
            return []
    
    def get_job_details_by_id(self,job_id):
        """Get job details by job ID"""
        try:
            job_details=self.api.get_job(job_id)
            return job_details
        except Exception as e:
            print(f"Error getting job details: {e}")
            return {}

def print_job_details(details):
    print("\n=== JOB DETAILS ===")
    print(f"Title: {details.get('title', 'N/A')}")
    print(f"Company: {details.get('companyDetails', {}).get('com.linkedin.voyager.deco.jobs.web.shared.WebCompactJobPostingCompany', {}).get('companyResolutionResult', {}).get('name', 'N/A')}")
    print(f"Location: {details.get('formattedLocation', 'N/A')}")
    
    workplace_type = details.get('workplaceTypesResolutionResults', {}).get('urn:li:fs_workplaceType:2', {}).get('localizedName', 'N/A')
    print(f"Workplace Type: {workplace_type}")
    
    description = details.get('description', {}).get('text', 'N/A')
    print(f"Description: {description[:200]}..." if len(description) > 200 else description)
    
    # Extract salary from description if present (since it's in the text)
    if "[$" in description:
        salary = description[description.find("[$"):].split("]")[0] + "]"
        print(f"Salary Range: {salary}")
    
    apply_method = {}
    
    apply_method = details.get('applyMethod', {}).get('com.linkedin.voyager.jobs.OffsiteApply', {})
    if apply_method == {}:
        apply_method = details.get('applyMethod', {}).get('com.linkedin.voyager.jobs.ComplexOnsiteApply', {})
    
    
    # it might be easyApplyUrl or companyApplyUrl
    
    if 'companyApplyUrl' in apply_method:
        print(f"Application Type: {'External Apply'}") 
        print(f"Apply URL: {apply_method.get('companyApplyUrl', 'N/A')}") 
    
    if 'easyApplyUrl' in apply_method:
        print(f"Application Type: {'Easy Apply'}") 
        print(f"Apply URL: {apply_method.get('easyApplyUrl', 'N/A')}") 
        
    
    listed_time = details.get('listedAt', 'N/A')
    print(f"Posted Date: {listed_time}")
    print(f"Job ID: {details.get('jobPostingId', 'N/A')}")
    print("\n" + "="*50)

def extract_job_details_using_regex_and_nlp(details):
    """Extract job details using regex and NLP"""
def main():
    search_params = {
    "keywords": "Software Engineer",
    "location_name": "United States",
    "remote": ["2"],  # Remote jobs only
    "experience": ["2", "3"],  # Entry level and Associate
    "job_type": ["F", "C"],  # Full-time and Contract
    "limit": 2,
    }
    
    job_search=JobSearch()
    jobs=job_search.search_jobs(search_params)
    
    
    for job in jobs:
        job_id = job["entityUrn"].split(":")[-1]
        details = job_search.get_job_details_by_id(job_id)
        # print(details)
        print_job_details(details)


if __name__=="__main__":
    main()