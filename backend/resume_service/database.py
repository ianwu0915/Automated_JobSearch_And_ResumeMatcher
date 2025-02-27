from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Database configuration
Database_url = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/job_db")
engine = create_engine(Database_url)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# Job Table Schema 
class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String, nullable=False)
    company = Column(String, nullable=False)
    location = Column(String, nullable=False)
    workplace_type = Column(String, nullable=False)
    skills = Column(Text, nullable=False)
    experience_level = Column(String, nullable=False)
    salary = Column(String, nullable=False)
    apply_url = Column(String, nullable=False)

Base.metadata.create_all(bind=engine)

def save_job(job_data):
    session = SessionLocal()
    job = Job(
        listed_date=job_data["listed_date"],
        job_title=job_data["job_title"],
        company=job_data["company"],
        location=job_data["location"],
        workplace_type=job_data["workplace_type"],
        skills=job_data["skills"],
        experience_level=job_data["experience_level"],
        salary=job_data["salary"],
        apply_url=job_data["apply_url"]
    )
    session.add(job)
    session.commit()
    session.close()
    
def get_jobs():
    session = SessionLocal()
    jobs = session.query(Job).all()
    session.close()
    return jobs
    