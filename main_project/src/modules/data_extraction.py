import re
import spacy
import pandas as pd
from typing import Dict, Any

# Load the spacy model
nlp=spacy.load("en_core_web_sm")

def extract_job_sections(job_description: str) -> Dict[str, Any]:
    job_sections = {}
    
    sections = {
        "title": None,
        "company": None,
        "location": None,
        "workplace_type": None,
        "salary": None,
        "application_link": None,
        "responsibilities": None,
        "qualifications": None,
        "preferred_qualifications": None,
        "skills": None
    }
    
    # Patterns to match different sections (customized based on variation in job posting)
    patterns = {
        "title": r"(?i)(?:Position|Job Title)[:\s]*(.*)",
        "company": r"(?i)(?:Company)[:\s]*(.*)",
        "location": r"(?i)(?:Location)[:\s]*(.*)",
        "workplace_type": r"(?i)(?:Workplace Type)[:\s]*(.*)",
        "salary": r"(?i)(?:Pay|Salary)[:\s]*(.*)",
        "application_link": r"(?i)(?:Apply|Application Link)[:\s]*(https?://[\w./-]+)",
        "responsibilities": r"(?i)(?:Responsibilities|Key Responsibilities|Duties).*?\n(.*?)\n(?:Qualifications|Requirements|Preferred|\Z)",
        "qualifications": r"(?i)(?:Qualifications|Requirements).*?\n(.*?)\n(?:Preferred|\Z)",
        "preferred_qualifications": r"(?i)(?:Preferred Qualifications).*?\n(.*?)\n(?:Cool Things|\Z)",
        "skills": r"(?i)(?:Skills|Technical Skills).*?\n(.*?)\n(?:Responsibilities|Duties|\Z)"
    }
    
    
    
    return job_sections
    
    
    
