# app/core/database.py
import psycopg2
import redis
import json
import logging
import hashlib
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from datetime import datetime

from backend.core.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Redis connection
redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=0,
    decode_responses=True,
    password=settings.REDIS_PASSWORD if hasattr(settings, 'REDIS_PASSWORD') else None
)

def get_db_connection():
    """
    Create and return a connection to the PostgreSQL database.
    """
    try:
        connection = psycopg2.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            dbname=settings.DB_NAME,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD
        )
        # Set autocommit to False to manage transactions explicitly
        connection.autocommit = False
        
        return connection
    except Exception as e:
        logging.error(f"Database connection error: {str(e)}")
        raise Exception(f"Failed to connect to database: {str(e)}")

@contextmanager
def get_db_cursor(commit=False):
    """
    Context manager for database connections.
    Automatically handles connection cleanup and optionally commits.
    
    Usage:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT * FROM table")
            results = cursor.fetchall()
    """
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=RealDictCursor) # return results as dictionaries
        yield cursor  # yield: return the cursor object to the caller
        if commit:
            connection.commit()
    except Exception as e:
        if connection:
            connection.rollback()
        logging.error(f"Database error: {str(e)}")
        raise
    finally:
        if connection:
            cursor.close()
            connection.close()

def execute_query(query, params=None, fetch_one=False):
    """
    Execute a query and return results.
    # Example usage:
    resume = execute_query(
        "SELECT * FROM user_resumes WHERE resume_id = %s", 
        (resume_id,), 
        fetch_one=True
    )
    """
    with get_db_cursor() as cursor:
        cursor.execute(query, params or ())
        if fetch_one:
            return cursor.fetchone()
        return cursor.fetchall()

def execute_with_commit(query, params=None):
    """
    Execute a query with commit (for INSERT, UPDATE, DELETE).
    Returns True if successful, False otherwise.
    """
    try:
        with get_db_cursor(commit=True) as cursor:
            cursor.execute(query, params or ())
            return True
    except Exception as e:
        logger.error(f"Error executing query with commit: {str(e)}")
        return False

# Redis cache helpers
def cache_set(key, value, expiry=3600):
    """
    Set a value in Redis cache with expiry time in seconds.
    Serializes complex objects automatically.
    """
    try:
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        return redis_client.set(key, value, ex=expiry)
    except Exception as e:
        logger.error(f"Redis cache set error: {str(e)}")
        return False

def cache_get(key):
    """
    Get a value from Redis cache.
    Attempts to deserialize JSON strings automatically.
    """
    try:
        value = redis_client.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return None
    except Exception as e:
        logger.error(f"Redis cache get error: {str(e)}")
        return None

def cache_delete(key):
    """
    Delete a key from Redis cache.
    """
    try:
        return redis_client.delete(key)
    except Exception as e:
        logger.error(f"Redis cache delete error: {str(e)}")
        return False

def generate_cache_key(prefix, identifier):
    """
    Generate a consistent cache key with a prefix and identifier.
    """
    return f"{prefix}:{identifier}"

# Initialize database tables
def initialize_database():
    """
    Initialize database tables and indices.
    Call this function when starting the application.
    """
    logger.info("Starting database initialization...")
    with get_db_cursor(commit=True) as cursor:
        # Create user_resumes table
        logger.info("Creating user_resumes table if not exists...")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_resumes (
            id SERIAL PRIMARY KEY,
            user_id VARCHAR(50) NOT NULL,
            resume_id VARCHAR(50) UNIQUE NOT NULL,
            skills JSONB,
            years_experience VARCHAR(50),
            education JSONB,
            word_frequencies JSONB,
            raw_text TEXT,
            created_at TIMESTAMP NOT NULL DEFAULT NOW()
        )
        """)
        
        # Create jobs table
        logger.info("Creating jobs table if not exists...")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id SERIAL PRIMARY KEY,
            job_id VARCHAR(50) UNIQUE NOT NULL,
            title VARCHAR(255) NOT NULL,
            company VARCHAR(255) NOT NULL,
            location VARCHAR(255),
            workplace_type VARCHAR(50),
            description TEXT,
            required_skills JSONB,
            required_experience VARCHAR(50),
            required_education JSONB,
            word_frequencies JSONB,
            apply_url TEXT,
            listed_time VARCHAR(50),
            source VARCHAR(50) DEFAULT 'linkedin',
            created_at TIMESTAMP NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMP NOT NULL DEFAULT NOW()
        )
        """)
        
        # Create match_results table to store match history
        logger.info("Creating match_results table if not exists...")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS match_results (
            id SERIAL PRIMARY KEY,
            resume_id VARCHAR(50) NOT NULL,
            job_id VARCHAR(50) NOT NULL,
            overall_match FLOAT NOT NULL,
            skills_match FLOAT,
            experience_match FLOAT,
            education_match FLOAT,
            contextual_match FLOAT,
            missing_skills JSONB,
            created_at TIMESTAMP NOT NULL DEFAULT NOW(),
            UNIQUE(resume_id, job_id)
        )
        """)
        
        # Create indexes for faster queries
        logger.info("Creating indexes...")
        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_user_resumes_user_id ON user_resumes(user_id);
        CREATE INDEX IF NOT EXISTS idx_user_resumes_resume_id ON user_resumes(resume_id);
        CREATE INDEX IF NOT EXISTS idx_jobs_job_id ON jobs(job_id);
        CREATE INDEX IF NOT EXISTS idx_jobs_company ON jobs(company);
        CREATE INDEX IF NOT EXISTS idx_match_results_resume_id ON match_results(resume_id);
        CREATE INDEX IF NOT EXISTS idx_match_results_job_id ON match_results(job_id);
        """)
        
        logger.info("Database initialization completed successfully!")