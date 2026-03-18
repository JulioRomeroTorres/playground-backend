from pydantic import BaseModel, Field
from typing import Optional

from app.domain.contants import TypeDeploymentClient

class DefualtLlmSettings:
    temperature: float = 0.7
    output_tokens_limit: int = 2048
    top_k: int = 40
    top_p: float = 0.9
    model: str = "gpt-4o-mini"

class LlmSettings(BaseModel):
    temperature: Optional[float] = Field(default=DefualtLlmSettings.temperature)
    output_tokens_limit: Optional[int] = Field(default=DefualtLlmSettings.output_tokens_limit)
    top_k: Optional[int] = Field(default=DefualtLlmSettings.top_k)
    top_p: Optional[float] = Field(default=DefualtLlmSettings.top_p)
    endpoint: Optional[str] = Field(default=None)
    api_key: Optional[str] = Field(default=None)    
    model: Optional[str] = Field(default=DefualtLlmSettings.model)
    version: Optional[str] = Field(default=None)
    deployment_type: Optional[TypeDeploymentClient] = Field(default=TypeDeploymentClient.AGENT_FRAMEWORK)
    agent_id: Optional[str] = Field(default=None)