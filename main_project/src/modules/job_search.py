from linkedin_api import Linkedin
from dotenv import load_dotenv
import os
import pandas as pd
import json
from pathlib import Path
from main_project.src.modules.data_processing.job_data_extraction import extract_job_sections

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
    # print(f"Description: {description[:200]}..." if len(description) > 200 else description)
    
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


def main():
    search_params = {
    "keywords": "Software Engineer",
    "location_name": "United States",
    "remote": ["2"],  # Remote jobs only
    "experience": ["2", "3"],  # Entry level and Associate
    "job_type": ["F", "C"],  # Full-time and Contract
    "limit": 5,
    }
    
    job_search=JobSearch()
    jobs=job_search.search_jobs(search_params)
    
    extract_datas = {}
    
    for job in jobs:
        job_id = job["entityUrn"].split(":")[-1]
        details = job_search.get_job_details_by_id(job_id)
        # skills = job_search.api.get_job_skills(job_id) -> match your linkedin profile skill with jd 
        # print(skills)
        # print(details)
        print_job_details(details)
        
        description = details.get('description', {}).get('text', '')
        if description:
            # print(description)
            extract_detail = extract_job_sections(description)
        print("-----------------------------")
        # print(extract_detail)
        extract_datas[job_id] = extract_detail
        
    # Create output directory if it doesn't exist
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

    # Convert to DataFrame and transpose for better readability
    df = pd.DataFrame(extract_datas).T  # Transpose to have job IDs as index

    # Save data with error handling
    try:
        # Save to JSON
        json_path = output_dir / "job_data.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(extract_datas, f, indent=4, ensure_ascii=False)

        # Save to Excel
        excel_path = output_dir / "job_data.xlsx"
        df.to_excel(excel_path, index=True, index_label="Job ID")
        
        print(f"Data saved successfully to:\n- {json_path}\n- {excel_path}")
    except Exception as e:
        print(f"Error saving data: {e}")

    
if __name__=="__main__":
    main()