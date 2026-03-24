from pydantic import BaseModel
from typing import Optional, Any, List
from datetime import datetime

from app.domain.utils import (
    format_datetime_to_str
) 

class SimplifyWorkflowInformation(BaseModel):
    workflow_id: str
    name: str
    description: Optional[str] = None
    created_at: Optional[datetime] = None

    def format_json(self):
        return {
            "workflow_id": self.workflow_id,
            "description": self.description,
            "name": self.name,
            "created_at": format_datetime_to_str(self.created_at)
        }

    pass

class AgenticEdge(BaseModel):
    source: str
    target: str

class AgenticNode(BaseModel):
    id: str
    type: str
    sub_type: Optional[str] = None
    sub_agents: Optional[List[str]] = None

class CompletedWorkflowInformation(BaseModel):

    name: str
    start_node: str
    execution_config: Any
    unique_agents_ids: Optional[List[str]]
    nodes: Optional[List[AgenticNode]] = []
    edges: Optional[List[AgenticEdge]] = []
    created_at: datetime

    def format_json(self):
        return {
            "name": self.name,
            "start_node": self.start_node,
            "unique_agents_ids": self.unique_agents_ids,
            "nodes": [ node.model_dump() for node in self.nodes ],
            "edges": [ edge.model_dump() for edge in self.edges ],
            "created_at": format_datetime_to_str(self.created_at)
        }