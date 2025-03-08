from pydantic import BaseModel
from typing import List, Dict
from humps import camelize

def to_camel(string):
    return camelize(string)

class ResumeData(BaseModel):
    user_id: str
    resume_id: str
    skills: List[str] = []
    experience: List[Dict] = []
    education: List[Dict] = []
    projects: List[Dict] = []
    raw_text: str = ""
    
    class Config:
        populate_by_name = True
        alias_generator = to_camel
    
# Job structure model
class JobData(BaseModel):
    job_id: str
    title: str
    company: str
    location: str
    workplace_type: str
    listed_time: str
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
    created_at: str
