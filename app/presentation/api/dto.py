
from typing import Any, Optional, List, Dict, Any
from pydantic import BaseModel, Field
from app.domain.utils import get_current_datetime

from enum import Enum

class OrderEnum(Enum):
    ASC = 'ASC'
    DESC = 'DESC'

class Message(BaseModel):
    role: str = Field(description="Role of the message sender (user, assistant, system)")
    content: str = Field(description="Message content")

class AgentTrace(BaseModel):
    identity_id: Optional[str] = Field(
        default=None,
        description="User id"
    )
    identity_type: Optional[str] = Field(
        default=None,
        description="Bussiness Unit"
    )
    identity_domain: Optional[str] = Field(
        default=None,
        description="Bussiness domian"
    )
    identity_subdomain: Optional[str] = Field(
        default=None,
        description="Bussiness subdomian"
    )
    
    identity_parent_session_id:  Optional[str] = Field(
        default=None,
        description="Interaction id"
    )

    def to_json(self)-> Dict[str, Any]:
        return {
            "identity.id": self.identity_id,
            "identity.type": self.identity_type,
            "identity.domain": self.identity_domain,
            "identity.subdomain": self.identity_subdomain
        }

class AgentInformationRequest(BaseModel):
    name: str = Field(decription="Agent Name")
    description: Optional[str] = Field(description="Agent Description", default="")
    version: Optional[str] = Field(description="Agent Version", default="v1")
    tools_ids: Optional[List[str]] = Field(description="Tools Ids", default=[])
    enable_memory: Optional[bool] = Field(description="Enable Long Memory", default= False)

class ToolInformationRequest(BaseModel):
    name: str = Field(decription="Agent Name")
    description: str = Field(description="Agent Description")
    input_params: Optional[Dict[str, Any]] = Field(description="Input Params", default=None)
    logic_content: str = Field(description="Logic content of tool")

class PrimitiveConversationInformation(BaseModel):
    message: str = Field(description="Current user message")
    additional_files: Optional[List[str]] = Field(
        default_factory=list,
        description="List of attached files"
    )

class ConversationRequest(PrimitiveConversationInformation):
    trace: AgentTrace = Field(
        description="trace information"
    )
    additional_information: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Additional Params"
    )
    
class ConversationResponse(BaseModel):
    type: str = Field(description="Response type", default="text")
    content: str = Field(description="Response message")
    timestamp: str = Field(description="Response timestamp", default=get_current_datetime())
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class CommonFilterParams(BaseModel):
    page: Optional[int] = 0
    limit: Optional[int] = 10
    order: Optional[str] = OrderEnum.DESC.value

class ConversationFilters(CommonFilterParams):
    pass
    
class UploadedDocumentResponse(BaseModel):
    generated_img_files: List[str] = Field(description="List of image file from pdf page")
    file_name: str = Field(description="List of file name")