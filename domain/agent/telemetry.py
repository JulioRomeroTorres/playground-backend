from enum import Enum
from app.config import get_settings
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from agent_framework import ChatMessage

class AgentTypeEnum(Enum):
    MODEL_BASE_LLM = 'Modelo Base LLM'
    EPHIMERAL_AGENT = 'Ephimeral Agent'
    MOTOR_AGENT_PROVIDER = 'Motor Agente Proveedor'
    CLASSIC_AGENT = 'Agent'

class AgentOperationEnum(Enum):
    CHAT = 'Chat'

class TelemetryProperties(BaseModel):
    agent_conversation_id: str = Field(alias = "agent.conversation.id", description="Agent Conversation Id")
    agent_id: str = Field(alias = "agent.id", description="Agent Id")
    agent_name: str = Field(alias="agent.name", description="Agent Name")
    agent_version: Optional[str] = Field(alias= "agent.version", description="Agent Version", default=get_settings().api_version)
    
    request_model: str = Field(alias="request.model", description="Request model", examples=["gpt-4o-mini"])
    operation_name: Optional[AgentOperationEnum] = Field(alias="operation.name", description="Operation ", examples=['chat'], default=AgentOperationEnum.CHAT)
    agent_type: Optional[AgentTypeEnum] = Field(alias="agent.type", description="Agent type", default=AgentTypeEnum.EPHIMERAL_AGENT)
    
    input_messages: Optional[List[Any]] = Field(alias="input.messages", description="Input messages of agent during the interaction", default=None)
    input_tokens: Optional[int] = Field(alias="input.tokens", description="Input tokens during the request", default=None)
    output_messages: Optional[List[Any]] = Field(alias="output.messages", description="Output message from agent", default=None)
    output_tokens: Optional[int] = Field(alias="output.tokens", description="Output tokens after the request", default=None)
    cached_tokens: Optional[int] = Field(alias="cached.tokens", description="Cached tokens of model", default=None)

    def _format_chat_message(self, message: ChatMessage) -> Dict[str, Any]:
        return message.to_dict()

    def _format_list_chat_message(self, messages: List[ChatMessage]) -> List[Dict[str, Any]]:
        
        return [ self._format_chat_message(message) for message in  messages ] if messages else []

    def format_json(self):
        
        return {
            "agent.conversation.id": self.agent_conversation_id,
            "agent.id": self.agent_id,
            "agent.name": self.agent_name,
            "agent.version": self.agent_version,
            "request.model": self.request_model,
            "operation.name": self.operation_name.value,
            "agent.type": self.agent_type.value,
            "input.messages": self._format_list_chat_message(self.input_messages),
            "input.tokens": self.input_tokens,
            "output.messages": self._format_list_chat_message(self.output_messages),
            "output.tokens": self.output_tokens,
            "cached.tokens": self.cached_tokens,
        }
    