from pydantic import BaseModel
from humps import camelize
from datetime import datetime
class BaseModelConfig(BaseModel):
    class Config:
        from_attributes = True
        alias_generator = camelize
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        } 