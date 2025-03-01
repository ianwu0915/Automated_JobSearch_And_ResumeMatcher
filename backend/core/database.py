import psycopg2
import logging
from psycopg2.extras import RealDictCursor
from backend.core.config import settings

from contextlib import contextmanager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

# Optional: Function to initialize the database tables
def initialize_database():
    """
    Initialize database tables if they don't exist.
    Call this function when starting the application.
    """
    logger.info("Starting database initialization...")
    with get_db_cursor(commit=True) as cursor:
        # Create tables if they don't exist
        logger.info("Creating user_resumes table if not exists...")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_resumes (
            id SERIAL PRIMARY KEY,
            user_id VARCHAR(50) NOT NULL,
            resume_id VARCHAR(50) UNIQUE NOT NULL,
            skills JSONB,
            experience JSONB,
            education JSONB,
            projects JSONB,
            raw_text TEXT,
            created_at TIMESTAMP NOT NULL DEFAULT NOW()
        )
        """)
        
        # Create indexes for faster queries
        logger.info("Creating indexes...")
        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_user_resumes_user_id ON user_resumes(user_id);
        CREATE INDEX IF NOT EXISTS idx_user_resumes_resume_id ON user_resumes(resume_id);
        """)
        
        logger.info("Database initialization completed successfully!")

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
    
