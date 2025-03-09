from pydantic import BaseModel
from humps import camelize
from datetime import datetime
class BaseModelConfig(BaseModel):
    class Config:
        # Allows creating model from ORM objects (e.g., SQLAlchemy models)
        from_attributes = True
        
        # Converts snake_case to camelCase in JSON output
        # alias_generator = camelize
        
        # Allows populating models using either the alias or the original name
        populate_by_name = True
        
        # Custom JSON encoders for specific types
        json_encoders = {
            datetime: lambda v: v.isoformat()  # Converts datetime to ISO format string
        } 