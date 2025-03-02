import os
import uuid
import tempfile
from fastapi import UploadFile, HTTPException
import aiofiles
from datetime import datetime
from pathlib import Path
import mimetypes 
from typing import Union, BinaryIO

from ..utils.file_processors import extract_text_from_file, SUPPORTED_MIME_TYPES
from .feature_service import FeatureService

class ResumeService:
    def __init__(self, feature_service: FeatureService):
        self.feature_service = feature_service
        self.supported_mime_types = SUPPORTED_MIME_TYPES

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
            
            # Extract features using FeatureService
            features = self.feature_service.extract_resume_features(resume_text)
            
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
