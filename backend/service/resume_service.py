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
    
    async def process_resume(self, file: UploadFile, user_id: str):
        """Process resume from FastAPI UploadFile"""
        try:
            # Validate file type
            content_type = file.content_type
            if content_type not in self.supported_mime_types:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Unsupported file type: {content_type}. Supported types: {', '.join(self.supported_mime_types.keys())}"
                )
            
            file_type = self.supported_mime_types[content_type]
            resume_id = str(uuid.uuid4())
            
            # Save file temporarily
            temp_file_path = os.path.join(tempfile.gettempdir(), f"{resume_id}.{file_type}")
            async with aiofiles.open(temp_file_path, 'wb') as out_file:
                while content := await file.read(1024 * 1024):  # 1MB chunks
                    await out_file.write(content)
            
            return await self._process_resume_file(temp_file_path, user_id, file_type, resume_id, cleanup=True)
                    
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error processing resume: {str(e)}"
            )

    async def process_resume_file(self, file_path: str, user_id: str, content_type: str = None):
        """Process resume from file path"""
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
            
            return await self._process_resume_file(file_path, user_id, file_type, resume_id, cleanup=False)
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error processing resume: {str(e)}"
            )

    async def _process_resume_file(self, file_path: str, user_id: str, file_type: str, resume_id: str, cleanup: bool = False):
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
                "features": features  # Unpack features into result
            }
            
            return result
            
        finally:
            # Clean up temporary file if needed
            if cleanup and os.path.exists(file_path):
                os.remove(file_path)