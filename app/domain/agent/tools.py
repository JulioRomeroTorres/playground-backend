
from typing import Dict, Optional
from pydantic import BaseModel, Field
from typing import List, Any

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