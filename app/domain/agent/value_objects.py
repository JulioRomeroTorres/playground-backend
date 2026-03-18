from pydantic import BaseModel, ConfigDict, Field


class DraftAgentOutput(BaseModel):
    model_config = ConfigDict(extra='forbid')

    draft_type: str = Field(
        description="Type of draft: email, document, report, letter"
    )
    content: str = Field(description="The drafted content")
    subject: str | None = Field(default=None, description="Subject line if applicable")
    tone: str = Field(
        default="professional", description="Tone of the draft: professional, casual, formal"
    )


class RagAgentOutput(BaseModel):
    model_config = ConfigDict(extra='forbid')

    query: str = Field(description="The original query")
    answer: str = Field(description="The generated answer")
    sources: list[str] = Field(
        default_factory=list, description="List of source references"
    )
    confidence: float = Field(
        description="Confidence in the answer", ge=0.0, le=1.0, default=0.8
    )

class GenIaOutput(BaseModel):
    model_config = ConfigDict(extra='forbid')

    query: str = Field(description="The original query")
    answer: str = Field(description="The generated answer")
    sources: list[str] = Field(
        default_factory=list, description="List of source references"
    )
    confidence: float = Field(
        description="Confidence in the answer", ge=0.0, le=1.0, default=0.8
    )


class MailboxAgentOutput(BaseModel):
    model_config = ConfigDict(extra='forbid')

    action: str = Field(
        description="Action performed: redirect, respond, assist",
        default="redirect"
    )
    result: str = Field(
        description="Full response message to the user"
    )
    summary: str | None = Field(
        default=None,
        description="Brief summary of the interaction"
    )

class ManagerAgentOutput(BaseModel):
    model_config = ConfigDict(extra='forbid')

    sub_agent_name: str = Field(
        default="mail_box",
        description="Brief summary of the interaction"
    )