from fastapi import APIRouter, HTTPException, File, UploadFile, Query
from typing import List
import os

from backend.service.redis_service import RedisClient
from backend.service.resume_service import ResumeService
from backend.service.job_service import JobService
from backend.service.matching_service import MatchingService

router = APIRouter(prefix="/api")

# Service instances
resume_service = ResumeService()
job_service = JobService()
matching_service = MatchingService(resume_service, job_service)

@router.get("/")
async def hello_world():
    return {"message": "Hello World"}

@router.post("/resumes/upload", tags=["resumes"])
async def upload_resume(
    file: UploadFile = File(...),
    user_id: str = Query(..., description="User ID for the resume") # /api/resumes/upload?user_id=1
):
    """
    Upload and process a resume file.
    The processed resume will be stored in the database and used for subsequent job matching.
    """
    try:
        # Save file temporarily
        temp_dir = "temp"
        os.makedirs(temp_dir, exist_ok=True)
        file_path = os.path.join(temp_dir, file.filename) # temp/resume.pdf
        
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
            resume_id = await resume_service.save_resume(resume_data)
            
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
        
@router.get("/resumes/{user_id}", tags=["resumes"])
async def get_latest_resume_by_user_id(user_id: str):
    resume = await resume_service.get_resume_by_user_id(user_id)
    return resume

@router.get("/jobs/search_and_match", tags=["jobs", "matching"])
async def search_jobs_and_match(
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
        resume = await resume_service.get_resume_by_user_id(user_id)
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
           await job_service.save_job(job)
            
        
        # Match jobs with resume
        matches = await matching_service.match_resume_to_jobs(  
            # Assuming resume path is stored
            jobs,
            user_id
        )
        
        # Store match results
        await matching_service.store_match_results(matches)
        
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

@router.get("/jobs/{job_id}", tags=["jobs"])
async def get_job(job_id: str):
    """
    Get details for a specific job, including any cached match results.
    """
    try:
        # Try to get from cache/database
        job = await job_service.get_job_by_id(job_id)
        if not job:
            # If not found, fetch from LinkedIn
            job = await job_service.get_job_by_id(job_id)
            if job:
                await job_service.save_job(job)
        
        return job
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving job: {str(e)}"
        )

@router.get("/matches/history", tags=["matching"])
async def get_match_history(
    user_id: str = Query(..., description="User ID to get match history for"),
    limit: int = Query(50, description="Maximum number of matches to return"),
    min_score: int = Query(50, description="Minimum match score to return")
):
    """
    Get historical match results for a user.
    """
    try:
        matches = await matching_service.get_job_and_matches_for_resume(user_id, limit, min_score)
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
