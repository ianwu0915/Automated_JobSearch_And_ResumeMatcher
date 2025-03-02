from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, BackgroundTasks, Query
from typing import Dict, Any, List, Optional
import uuid
import os
import tempfile
import aiofiles
from datetime import datetime, timedelta

from backend.core.database import get_db_cursor, redis_client, execute_query, execute_with_commit
from backend.utils.file_processors import SUPPORTED_MIME_TYPES
from backend.service.resume_service import process_resume_background, ResumeService
from backend.service.redis_service import RedisService
from backend.service.job_service import JobService
from backend.service.matching_service import MatchingService
from backend.service.feature_service import FeatureService
from backend.repository.resumeRepository import ResumeRepository
from backend.repository.jobRepository import JobRepository
from backend.repository.matchRepository import MatchRepository

router = APIRouter(prefix="/api", tags=["resumes"])
redis_service = RedisService()

# Service instances
feature_service = FeatureService()
resume_service = ResumeService(feature_service)
job_service = JobService(feature_service, redis_client)
matching_service = MatchingService(resume_service, job_service)

# Repository instances
resume_repo = ResumeRepository()
job_repo = JobRepository()
match_repo = MatchRepository()

@router.get("/")
async def hello_world():
    return {"message": "Hello World"}

@router.post("/resumes/upload")
async def upload_resume(
    file: UploadFile = File(...),
    user_id: str = Query(..., description="User ID for the resume")
):
    """
    Upload and process a resume file.
    The processed resume will be stored in the database and used for subsequent job matching.
    """
    try:
        # Save file temporarily
        temp_dir = "temp"
        os.makedirs(temp_dir, exist_ok=True)
        file_path = os.path.join(temp_dir, file.filename)
        
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        try:
            # Process resume
            resume_data = await resume_service.process_resume_file(
                file_path,
                user_id,
                file.content_type
            )
            
            # will get resume_id, user_id, raw_text, processed_date, features
            # features is a dictionary with the following keys:
            # - skills: list of skills
            # - years_of_experience: int
            # - word_frequency: list of word_frequencies
    
            
            # Store database and redis cache
            resume_id = await resume_repo.save_resume(resume_data)
            
            return {
                "message": "Resume uploaded and processed successfully",
                "resume_id": resume_id,
                "features": resume_data["features"]
            }
            
        finally:
            # Clean up temporary file
            if os.path.exists(file_path):
                os.remove(file_path)
                
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing resume: {str(e)}"
        )
        
@router.get("/resumes/{resume_id}")
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

@router.get("/jobs/search")
async def search_jobs(
    keywords: str = Query(..., description="Job search keywords"),
    location: str = Query("United States", description="Location for job search"),
    experience_level: List[str] = Query(["2", "3"], description="Experience level codes"),
    job_type: List[str] = Query(["F", "C"], description="Job type codes (F=Full-time, C=Contract)"),
    remote: List[str] = Query(["2"], description="Remote work codes"),
    limit: int = Query(50, description="Maximum number of jobs to return"),
    user_id: str = Query(..., description="User ID for matching with uploaded resume")
):
    """
    Search for jobs and match them with the user's most recently uploaded resume.
    Returns jobs sorted by match score.
    """
    try:
        # Get user's most recent resume
        resume = await resume_repo.get_latest_resume(user_id)
        if not resume:
            raise HTTPException(
                status_code=404,
                detail="No resume found for this user. Please upload a resume first."
            )
        
        # Prepare search parameters
        search_params = {
            "keywords": keywords,
            "location_name": location,
            "experience": experience_level,
            "job_type": job_type,
            "remote": remote,
            "limit": limit
        }
        
        # Search for jobs
        jobs = await job_service.search_jobs_parallel([search_params])
        
        # Store jobs in database and cache if not already present
        for job in jobs:
            # Check if job exists in cache or database
            cached_job = await job_repo.get_job(job["job_id"])
            if not cached_job:
                await job_repo.save_job(job)
        
        resume = 
        
        # Match jobs with resume
        matches = await matching_service.match_resume_to_jobs(
            resume["resume_path"],  # Assuming resume path is stored
            jobs,
            user_id
        )
        
        # Store match results
        for match in matches:
            await match_repo.save_match_result({
                "resume_id": resume["resume_id"],
                "job_id": match["job_id"],
                "overall_match": match["match_score"],
                "match_details": match["match_details"]
            })
        
        return {
            "message": "Jobs found and matched successfully",
            "total_jobs": len(matches),
            "matches": matches
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error searching and matching jobs: {str(e)}"
        )

@router.get("/jobs/{job_id}")
async def get_job(job_id: str):
    """
    Get details for a specific job, including any cached match results.
    """
    try:
        # Try to get from cache/database
        job = await job_repo.get_job(job_id)
        if not job:
            # If not found, fetch from LinkedIn
            job = await job_service.get_job_by_id(job_id)
            if job:
                await job_repo.save_job(job)
        
        return job
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving job: {str(e)}"
        )

@router.get("/matches/history")
async def get_match_history(
    user_id: str = Query(..., description="User ID to get match history for"),
    limit: int = Query(50, description="Maximum number of matches to return")
):
    """
    Get historical match results for a user.
    """
    try:
        matches = await match_repo.get_user_matches(user_id, limit)
        return {
            "user_id": user_id,
            "total_matches": len(matches),
            "matches": matches
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving match history: {str(e)}"
        )
