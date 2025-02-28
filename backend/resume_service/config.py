# app/config.py
from pydantic import BaseModel
from functools import lru_cache
import os


class Settings(BaseModel):
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = os.getenv("DB_PORT", 5432)
    DB_NAME: str = os.getenv("DB_NAME", "resume_job_matching")
    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "password")

@lru_cache
def get_settings():
    return Settings()

settings = get_settings()
