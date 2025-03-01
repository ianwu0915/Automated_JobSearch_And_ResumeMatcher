from pydantic import BaseModel
from typing import List, Dict

# Resume structure model
class ResumeData(BaseModel):
    user_id: str
    resume_id: str
    skills: List[str] = []
    experience: List[Dict] = []
    education: List[Dict] = []
    projects: List[Dict] = []
    raw_text: str = ""