from typing import Any, Optional, Dict
from enum import Enum
from uuid import UUID, uuid4
from pydantic import BaseModel, Field

from app.domain.message import Message

class TypeStreamingResponseEnum(Enum):
    START = 'start'
    DATA = 'chunk'
    END = 'end'


class ConversationContext(BaseModel):
    session_id: UUID = Field(default_factory=uuid4, description="Unique conversation identifier")
    messages: list[Message] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class PrimitiveStreaming(BaseModel):
    type: str = Field(default=TypeStreamingResponseEnum.START.value, description="Type of response")

class StartStreamingResponse(PrimitiveStreaming):
    agent: str = Field(description="Agent Name")

class DataStreamingResponse(PrimitiveStreaming):
    text: str = Field(description="Partial data information")

class EndStreamingResponse(PrimitiveStreaming):
    metadata: Optional[Dict[str, Any]] = Field(default=dict(), description="Metadata of interaction")
