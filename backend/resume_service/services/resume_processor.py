from models import ResumeData
from database import get_db_cursor
from utils.ai_helpers import parse_resume_with_ai
from utils.file_processors import extract_text_from_file
from services.redis_service import RedisService
import json
import os

redis_service = RedisService()

async def process_resume_background(
    user_id: str, 
    resume_id: str, 
    file_path: str, 
    file_type: str
):
    try:
        resume_text = await extract_text_from_file(file_path, file_type)
        parsed_data = await parse_resume_with_ai(resume_text)
        
        resume_data = ResumeData(
            user_id=user_id,
            resume_id=resume_id,
            skills=parsed_data.get("skills", []),
            experience=parsed_data.get("experience", []),
            education=parsed_data.get("education", []),
            projects=parsed_data.get("projects", []),
            raw_text=resume_text
        )
        
        with get_db_cursor(commit=True) as cursor:
            cursor.execute(
                """
                INSERT INTO user_resumes (
                    user_id, resume_id, skills, experience, education, 
                    projects, raw_text, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
                """,
                (
                    resume_data.user_id,
                    resume_data.resume_id,
                    json.dumps(resume_data.skills),
                    json.dumps(resume_data.experience),
                    json.dumps(resume_data.education),
                    json.dumps(resume_data.projects),
                    resume_data.raw_text
                )
            )
        
        
        redis_service.set_resume_status(resume_id, "processed")
        
    except Exception as e:
        print(f"Error in background processing: {str(e)}")
        redis_service.set_resume_status(resume_id, f"failed:{str(e)}")
    finally:
        if os.path.exists(file_path):
            os.remove(file_path) 