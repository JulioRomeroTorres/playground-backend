from datetime import datetime
from typing import Any
from agent_framework import ChatMessage, UsageDetails
from pydantic import BaseModel, Field

class AgentResponse(BaseModel):
    message: str = Field(description="Response message text")
    agent_name: str = Field(description="Name of the agent that generated the response")
    intent: str | None = Field(default=None, description="Classified intent")
    confidence: float | None = Field(default=None, description="Confidence score")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = Field(default_factory=dict)

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