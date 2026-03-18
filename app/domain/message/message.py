from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field


class Message(BaseModel):
    role: str = Field(description="Message role: user or assistant")
    content: str = Field(description="Message content")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = Field(default_factory=dict)
