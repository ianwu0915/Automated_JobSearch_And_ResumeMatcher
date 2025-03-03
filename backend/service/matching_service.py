from typing import Dict, List, Any
from fastapi import HTTPException
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from backend.service.resume_service import ResumeService
from backend.service.job_service import JobService
from backend.repository.matchRepository import MatchRepository
from backend.core.database import initialize_database

class MatchingService:
    def __init__(self, resume_service: ResumeService, job_service: JobService):
        self.resume_service = resume_service
        self.job_service = job_service
        self.match_repo = MatchRepository()
    
    async def store_match_results(self, matches: List[Dict]):
        """Store match results in the database"""
        try:
            for match in matches:
                # Add user_id to match data
                match_data = {
                    "resume_id": match["resume_id"],
                    "job_id": match["job_id"],
                    "match_score": match["match_score"],
                    "matched_skills": match["matched_skills"],
                    "missing_skills": match["missing_skills"],
                    "required_experience_years": match["required_experience_years"],
                    "resume_experience_years": match["resume_experience_years"]
                }
                success = await self.match_repo.save_match_result(match_data)
                if not success:
                    raise Exception(f"Failed to save match result for job {match['job_id']}")
                    
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error storing match results: {str(e)}")
    
    async def get_job_and_matches_for_resume(self, resume_id: str, limit: int = 20, min_score: float = 50.0):
        """Get stored matches for a resume"""
        try:
            matches = await self.match_repo.get_job_and_matches_by_resume_id(resume_id, limit, min_score)
            return matches
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error getting matches: {str(e)}")
    
    async def match_resume_to_jobs(self, jobs: List[Dict], user_id: str = "1") -> List[Dict[str, Any]]:
        """Match a resume against multiple jobs and return ranked matches"""
        try:
            # Get resume by current user ID
            resume = await self.resume_service.get_resume_by_user_id(user_id)
            if not resume:
                raise HTTPException(status_code=404, detail="Resume not found")
            
            # Calculate match scores for each job
            matches = []
            for job in jobs:
                match_result = self.match_resume_with_job(resume, job)
                matches.append(match_result)
            
            # Sort by match score descending
            matches.sort(key=lambda x: x["match_score"], reverse=True)
            return matches
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error matching resume to jobs: {str(e)}"
            )
    
    def match_resume_with_job(self, resume: Dict, job: Dict) -> Dict[str, Any]:
        """Match a single resume with a single job"""
        try:
            # Calculate match score
            match_score = self._calculate_match_score(resume, job)
            
            # Get match details
            match_details = self._get_match_details(resume, job)
            
            return {
                "resume_id": resume["resume_id"],
                "job_id": job["job_id"],
                "match_score": int(match_score),
                "matched_skills": match_details["matched_skills"],
                "missing_skills": match_details["missing_skills"],
                "required_experience_years": match_details["experience_years"]["required"],
                "resume_experience_years": match_details["experience_years"]["resume"],
                "job": job
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error matching resume with job: {str(e)}"
            )
    
    def _calculate_match_score(self, resume: Dict, job: Dict) -> float:
        """Calculate overall match score between resume and job"""
        try:
            # Get features
            resume_features = resume.get("features", {})
            job_features = job.get("features", {})
            # print("resume_features", resume_features)
            # print("job_features", job_features)
            if not resume_features or not job_features:
                return 0.0
            
            # Calculate individual scores
            skill_score = self._calculate_skill_match(
                resume_features.get("skills", []),
                job_features.get("skills", [])
            )
            
            print("skill_score", skill_score)
            
            experience_score = self._calculate_experience_match(
                resume_features.get("work_experience_years", 0),
                job_features.get("required_experience_years", 0)
            )
            
            print("experience_score", experience_score)
            
            keyword_score = self._calculate_keyword_match(
                resume_features.get("word_frequencies", {}),
                job_features.get("word_frequencies", {})
            )
            
            print("keyword_score", keyword_score)
            
            # Weighted average of scores
            weights = {
                "skills": 0.5,
                "experience": 0.3,
                "keywords": 0.2
            }
            
            total_score = (
                skill_score * weights["skills"] +
                experience_score * weights["experience"] +
                keyword_score * weights["keywords"]
            )
            
            return round(total_score * 100, 2)  # Convert to percentage with 2 decimal places
            
        except Exception as e:
            print(f"Error calculating match score: {e}")
            return 0.0
    
    def _calculate_skill_match(self, resume_skills: List[str], job_skills: List[str]) -> float:
        """Calculate match score based on skills"""
        if not resume_skills or not job_skills:
            return 0.0
            
        # Convert to sets for efficient matching
        resume_skills_set = set(s.lower() for s in resume_skills)
        job_skills_set = set(s.lower() for s in job_skills)
        
        # Calculate matches
        matched_skills = resume_skills_set.intersection(job_skills_set)
        
        # Calculate score based on percentage of required skills matched
        if len(job_skills_set) == 0:
            return 0.0
            
        return len(matched_skills) / len(job_skills_set)
    
    def _calculate_experience_match(self, resume_years: float, required_years: float) -> float:
        """Calculate match score based on years of experience"""
        try:
            # Convert to float and handle None/null values
            resume_years = float(resume_years or 0)
            required_years = float(required_years or 0)
            
            if required_years == 0:
                return 1.0  # No experience required = perfect match
            
            if resume_years >= required_years:
                return 1.0  # Meeting or exceeding requirements = perfect match
            
            # Partial match if within 2 years of requirement
            if resume_years >= (required_years - 2):
                return 0.5 + ((resume_years - (required_years - 2)) / 4)
            
            return max(0.0, resume_years / required_years)
            
        except Exception as e:
            print(f"Error in experience match calculation: {e}")
            print(f"Resume years: {resume_years}, Required years: {required_years}")
            return 0.0
    
    def _calculate_keyword_match(self, resume_words: Dict[str, int], job_words: Dict[str, int]) -> float:
        """Calculate match score based on keyword frequency similarity"""
        if not resume_words or not job_words:
            return 0.0
            
        # Get all unique words
        all_words = set(resume_words.keys()).union(set(job_words.keys()))
        
        # Create frequency vectors
        resume_vector = np.array([resume_words.get(word, 0) for word in all_words])
        job_vector = np.array([job_words.get(word, 0) for word in all_words])
        
        # Normalize vectors
        resume_norm = np.linalg.norm(resume_vector)
        job_norm = np.linalg.norm(job_vector)
        
        if resume_norm == 0 or job_norm == 0:
            return 0.0
            
        resume_vector = resume_vector / resume_norm
        job_vector = job_vector / job_norm
        
        # Calculate cosine similarity
        similarity = cosine_similarity(
            resume_vector.reshape(1, -1),
            job_vector.reshape(1, -1)
        )[0][0]
        
        return max(0.0, min(1.0, similarity))
    
    def _get_match_details(self, resume: Dict, job: Dict) -> Dict[str, Any]:
        """Get detailed breakdown of the match"""
        resume_features = resume.get("features", {})
        job_features = job.get("features", {})
        
        # Get matched and missing skills
        resume_skills = set(s.lower() for s in resume_features.get("skills", []))
        job_skills = set(s.lower() for s in job_features.get("skills", []))
        
        matched_skills = resume_skills.intersection(job_skills)
        missing_skills = job_skills - resume_skills
        
        return {
            "matched_skills": sorted(list(matched_skills)),
            "missing_skills": sorted(list(missing_skills)),
            "experience_years": {
                "resume": resume_features.get("work_experience_years", 0),
                "required": job_features.get("required_experience_years", 0)
            }
        }
    

# Example usage
async def main():
    from redis import Redis
    
    # Initialize services
    initialize_database()
    resume_service = ResumeService()
    job_service = JobService()
    matching_service = MatchingService(resume_service, job_service)
    
    # Example resume 
    resume_path = "tests/sample_data/resume1.pdf"
    resume = await resume_service.process_resume_file(resume_path, "1")
    print("resume", resume)
    await resume_service.save_resume(resume)
    
    # Example jobs
    search_params_list = [
        {
            "keywords": "Software Engineer",
            "location_name": "United States",
            "remote": ["2"],
            "experience": ["2", "3"],
            "job_type": ["F", "C"],
            "limit": 10,
        },
        {
            "keywords": "Software Developer",
            "location_name": "United States",
            "experience": ["2", "3"],
            "job_type": ["F", "C"],
            "limit": 10,
        },
        {
            "keywords": "Backend",
            "location_name": "United States",
            "experience": ["2", "3"],
            "job_type": ["F", "C"],
            "limit": 10,
        }
    ]
    jobs = await job_service.search_jobs_parallel(search_params_list)
    for job in jobs:
        await job_service.save_job(job)
    
    # Get matches
    matches = await matching_service.match_resume_to_jobs(jobs, "1")
    
    # Store matches
    await matching_service.store_match_results(matches)
    
    # Print results
    print("\nMatch Results:")
    for match in matches:
        # Access job details through the job field
        print(f"\nJob: {match['job']['title']} at {match['job']['company']}")
        print(f"Match Score: {match['match_score']:.2f}")
        print("Matched Skills:", ", ".join(match['matched_skills']))
        print("Missing Skills:", ", ".join(match['missing_skills']))
        print(f"Required Experience: {match['required_experience_years']} years")
        print(f"Resume Experience: {match['resume_experience_years']} years")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())