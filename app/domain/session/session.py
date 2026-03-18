from typing import Optional
from pydantic import BaseModel, Field

class SessionResponse(BaseModel):
    session_id: str = Field(description="workflow session")
    created_at: str = Field(description="workflow session")