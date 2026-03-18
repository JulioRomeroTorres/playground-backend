from typing import Any, Literal, Optional
from pydantic import BaseModel, Field


IntentType = Literal["knowledge", "drafting", "general"]


class IntentClassification(BaseModel):
    intent: str = Field(
        description="Tipo de intención clasificada"
    )
    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Confianza de la clasificación (0-1)"
    )
    original_message: str = Field(
        description="Mensaje original del usuario"
    )
    reasoning: str = Field(
        default="",
        description="Razonamiento de la clasificación"
    )

class AgnosticAgentResponse(BaseModel):
    message: str
    can_handle: Optional[bool] = None
    agent_name: str

class RagResponse(BaseModel):
    message: str
    can_handle: bool
    agent_name: str = "rag_agent"


class DraftResponse(BaseModel):
    message: str
    can_handle: bool
    agent_name: str = "draft_agent"


class MailboxResponse(BaseModel):
    message: str
    agent_name: str = "mailbox_agent"


class WorkflowOutput(BaseModel):
    agent_name: str = Field(
        description="Nombre del agente que manejó la solicitud"
    )
    message: str = Field(
        description="Mensaje de respuesta al usuario"
    )
    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Nivel de confianza de la respuesta (0-1)"
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Metadata adicional sobre el procesamiento"
    )

class WorkflowChunkOutput(BaseModel):
    agent_name: str = Field(
        description="Nombre del agente que manejó la solicitud"
    )
    chunk: str = Field(
        description="Parte del mensaje"
    )
    is_final: bool = Field(
        default=False,
        description="Es el final del workflow"
    )