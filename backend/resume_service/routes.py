from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, BackgroundTasks
from typing import Dict, Any
import uuid
import os
import tempfile
import aiofiles

from database import get_db_cursor
from utils.file_processors import SUPPORTED_MIME_TYPES
from utils.resume_processor import process_resume_background
from utils.redis_service import RedisService

router = APIRouter(prefix="/api/resumes", tags=["resumes"])
redis_service = RedisService()

@router.get("/")
async def hello_world():
    return {"message": "Hello World"}

@router.post("/upload")
async def upload_resume(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    user_id: str = None
) -> Dict[str, Any]:
    """
    Upload and process a new resume
    """
    if not user_id:
        raise HTTPException(status_code=400, detail="User ID is required")
        
    # Check if file type is supported
    content_type = file.content_type
    if content_type not in SUPPORTED_MIME_TYPES:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported file type: {content_type}. Supported types: PDF, DOCX, DOC, TXT"
        )
    
    file_type = SUPPORTED_MIME_TYPES[content_type]
    resume_id = str(uuid.uuid4())
    
    # Save file temporarily
    temp_file_path = os.path.join(tempfile.gettempdir(), f"{resume_id}.{file_type}")
    async with aiofiles.open(temp_file_path, 'wb') as out_file:
        while content := await file.read(1024 * 1024):  # 1MB chunks
            await out_file.write(content)
    
    # Start background processing
    background_tasks.add_task(
        process_resume_background,
        user_id,
        resume_id,
        temp_file_path,
        file_type
    )
    
    return {
        "status": "processing",
        "message": "Resume upload successful and processing started",
        "resume_id": resume_id
    }

@router.get("/{resume_id}/status")
async def check_resume_status(resume_id: str) -> Dict[str, str]:
    """
    Check the processing status of a resume
    """
    status = redis_service.get_resume_status(resume_id)
    
    if not status:
        # Check database if not in cache
        with get_db_cursor() as cursor:
            cursor.execute(
                "SELECT resume_id FROM user_resumes WHERE resume_id = %s",
                (resume_id,)
            )
            result = cursor.fetchone()
            
        if result:
            status = "processed"
            redis_service.set_resume_status(resume_id, status)
        else:
            status = "not_found"
    
    return {"status": status}

@router.get("/{resume_id}")
async def get_resume(resume_id: str):
    with get_db_cursor() as cursor:
        cursor.execute(
            """
            SELECT user_id, resume_id, skills, experience, education, 
                   projects, raw_text, created_at 
            FROM user_resumes 
            WHERE resume_id = %s
            """,
            (resume_id,)
        )
        result = cursor.fetchone()
        
        if not result:
            raise HTTPException(status_code=404, detail="Resume not found")
        
        # Convert the RealDictRow to a regular dict and handle JSON fields
        return {
            "user_id": result["user_id"],
            "resume_id": result["resume_id"],
            "skills": result["skills"],  # PostgreSQL should handle JSON conversion
            "experience": result["experience"],
            "education": result["education"],
            "projects": result["projects"],
            "raw_text": result["raw_text"],
            "created_at": result["created_at"].isoformat() if result["created_at"] else None
        }
