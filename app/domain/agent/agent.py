from datetime import datetime
from typing import Any, List, Optional

from agent_framework import ChatMessage, UsageDetails
from pydantic import BaseModel, Field
from app.domain.agent.tools import (
    SimplifyToolInformation,
    CompletedToolInformation
) 

from app.domain.utils import get_current_datetime

class AgentResponse(BaseModel):
    message: str = Field(description="Response message text")
    agent_name: str = Field(description="Name of the agent that generated the response")
    intent: str | None = Field(default=None, description="Classified intent")
    confidence: float | None = Field(default=None, description="Confidence score")
    timestamp: str = Field(default= f"{get_current_datetime()}")
    metadata: dict[str, Any] = Field(default_factory=dict)
    model_name: Optional[str] = Field(default="")

class ApiExternalAgentMetadata(BaseModel):
    conversation_id: str 
    model_name: str
    usage_tokens: int
    message_id: str

class ExternalAgentResponse(BaseModel):
    type: str
    content: str
    metadata: ApiExternalAgentMetadata

    def get_messages(self) -> ChatMessage:        
        return ChatMessage(role='assistant',text=self.content)
        
    def get_usage_details(self) -> UsageDetails:
        return UsageDetails(output_token_count=self.metadata.usage_tokens) 

class ConversationResponse(BaseModel):
    conversation_id: str = Field(description="Conversation Id")
    created_at: str = Field(description="created_at")


class SimplifyAgentInformation(BaseModel):
    name: str
    agent_id: Optional[str] = ""
    version: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def format_json(self):
        return {
            "name": self.name,
            "version": self.version,
            "created_at": None if self.created_at is None else self.created_at.strftime("%d/%m/%Y %H:%M"),
            "updated_at": None if self.updated_at is None else self.updated_at.strftime("%d/%m/%Y %H:%M"),
            "agent_id": self.agent_id
        }

class CompletedAgentInformation(SimplifyAgentInformation):
    tools: Optional[List[SimplifyToolInformation]] = []
    prompt: Optional[str] = ""
    enable_memory: Optional[bool] = False
    
    def format_json(self):
        return {
            **super().format_json(),
            "prompt": self.prompt,
            "enable_memory": self.enable_memory,
            "tools": [ tool.format_json() for tool in self.tools ]
        }

class AgentSettings(BaseModel):
    name: str
    version: str
    system_instruction: str
    model: str
    tools: List[CompletedToolInformation]
