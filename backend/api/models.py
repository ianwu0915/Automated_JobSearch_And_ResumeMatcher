from pydantic import BaseModel
from typing import List, Dict

class ResumeData(BaseModel):
    user_id: str
    resume_id: str
    skills: List[str] = []
    experience: List[Dict] = []
    education: List[Dict] = []
    projects: List[Dict] = []
    raw_text: str = ""
    
# Job structure model
class JobData(BaseModel):
    job_id: str
    title: str
    company: str
    location: str
    workplace_type: str
    listed_date: str
    apply_url: str
    description: str
    features: Dict[str]
    processed_date: str
    created_at: str

class MatchResult(BaseModel):
    resume_id: str
    job_id: str
    match_score: float
    matched_skills: List[str]
    missing_skills: List[str]
    required_experience_years: float
    resume_experience_years: float
