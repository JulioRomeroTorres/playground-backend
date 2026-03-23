
from typing import Dict, Optional
from pydantic import BaseModel, Field
from typing import List, Any
from datetime import datetime

class InputParameter(BaseModel):
    name: str = Field(default="")
    type: str = Field(default="")
    description: str = Field(default="")
    required: bool = Field(default=False)

class ToolSettings(BaseModel):

    name: str = Field(default="")
    description: str = Field(default="")
    source_name: str = Field(default="")
    base_url: str = Field(default="")
    endpoint: str = Field(default="")
    input_parameters: Optional[Dict[str, Any]] = Field(default_factory=None)
    output_parameters: Optional[Dict[str, str]] = Field(default_factory=dict)
    cloud_provider: str = Field(default="")
    method: Optional[str] = Field(default="POST")
    target_scope: Optional[List[str]] = Field(default=[])
    user_token: Optional[str] = Field(default=None)
    logical_content: Optional[str] = Field(default=None)


class SimplifyToolInformation(BaseModel):
    name: str 
    alias: str
    tool_id: str
    description: Optional[str] = ""
    created_at: datetime
    updated_at: Optional[datetime] = None

    def format_json(self):
        return {
            "name": self.name,
            "alias": self.alias,
            "description": self.description,
            "created_at": self.created_at.strftime("%d/%m/%Y %H:%M"),
            "updated_at": None if self.updated_at is None else self.updated_at.strftime("%d/%m/%Y %H:%M"),
            "tool_id": self.tool_id
        }

class CompletedToolInformation(SimplifyToolInformation):
    logic_content: Optional[str] = ""
    input_params: Optional[Dict[str, Any]] = None 

    def format_json(self):
        return {
            **super().format_json(),
            "code": self.logic_content,
            "input_params": self.input_params,
        }