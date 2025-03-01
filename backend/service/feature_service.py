from typing import Dict, Any
from fastapi import HTTPException
from backend.utils.feature_extractors import FeatureExtractor

class FeatureService:
    def __init__(self):
        self.feature_extractor = FeatureExtractor()
    
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
    
    def extract_job_features(self, text: str) -> Dict[str, Any]:
        """Extract features from job description"""
        try:
            features = self.feature_extractor.extract_job_features(text)
            return {
                "required_experience_years": features["required_experience_years"],
                "skills": features["skills"],
                "word_frequencies": dict(list(features["word_frequencies"].items())[:100])
            }
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error extracting job features: {str(e)}"
            ) 