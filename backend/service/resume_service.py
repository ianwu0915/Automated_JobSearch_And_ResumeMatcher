import os
import uuid
import tempfile
from fastapi import UploadFile, HTTPException
import aiofiles
from datetime import datetime
from pathlib import Path
import mimetypes 
from backend.repository.resumeRepository import ResumeRepository
from backend.utils.feature_extractors import FeatureExtractor
from typing import Dict, Any
from ..utils.file_processors import extract_text_from_file, SUPPORTED_MIME_TYPES

class ResumeService:
    def __init__(self):
        self.feature_extractor = FeatureExtractor()
        self.supported_mime_types = SUPPORTED_MIME_TYPES
        self.resume_repo = ResumeRepository()
        
    def extract_resume_features(self, text: str) -> Dict[str, Any]:
        """Extract features from resume text"""
        try:
            features = self.feature_extractor.extract_resume_features(text)
            return {
                "work_experience_years": features["work_experience_years"],
                "skills": features["skills"],
                "word_frequencies": dict(list(features["word_frequencies"].items())[:100])
            }
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error extracting resume features: {str(e)}"
            )

    async def process_resume_file(self, file_path: str, user_id: str, content_type: str = None):
        """
        Process resume from file path
        return a dictionary with the resume id, user id, raw text, processed date, 
        and features (skills, years_of_experience, work_frequency)
        """
        try:
            if not content_type:
                content_type = mimetypes.guess_type(file_path)[0]
            
            if content_type not in self.supported_mime_types:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Unsupported file type: {content_type}. Supported types: {', '.join(self.supported_mime_types.keys())}"
                )
            
            file_type = self.supported_mime_types[content_type]
            resume_id = str(uuid.uuid4())
            
            return await self._process_resume_file(file_path, user_id, file_type, resume_id)
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error processing resume: {str(e)}"
            )

    async def _process_resume_file(self, file_path: str, user_id: str, file_type: str, resume_id: str):
        """Internal method to process resume file"""
        try:
            # Extract text from file
            resume_text = await extract_text_from_file(file_path, file_type)
            
            # Extract features
            features = self.extract_resume_features(resume_text)
            
            # Create result object
            result = {
                "resume_id": resume_id,
                "user_id": user_id,
                "raw_text": resume_text,
                "processed_date": datetime.now().isoformat(),
                "features": features  
            }
            
            return result
        
        except Exception as e:
            print(f"Error processing resume: {str(e)}")
            raise e

    async def get_resume_by_user_id(self, user_id: str):
        """Get resume by ID"""
        try:
            resume = await self.resume_repo.get_resume_by_userid(user_id)
            return resume
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error getting resume: {str(e)}")
    
    async def save_resume(self, resume_data: dict):
        """Save resume to database"""
        try:
            await self.resume_repo.save_resume(resume_data)
            return resume_data["resume_id"]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error saving resume: {str(e)}")
