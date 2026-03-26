from abc import ABC, abstractmethod
from typing import Any, AsyncIterable, TYPE_CHECKING, Optional, List
from app.domain.agent.agent import AgentSettings, WorkflowSettings
from agent_framework import (
    WorkflowEvent,
    WorkflowRunResult
)

if TYPE_CHECKING:
    from app.domain.agent import AgentResponse

class IWorkflowOrchestrator(ABC):

    @abstractmethod
    def create_agent(agent_settings: AgentSettings, conversation_id: Optional[str] = None) -> None:
        pass

    @abstractmethod
    def create_sub_workflow(self, sub_workflow_settings: WorkflowSettings) -> None:
        pass

    @abstractmethod
    def build_workflow(self, workflow_structure: Any) -> None:
        pass

    @abstractmethod
    async def generate_stream_content(self, message: str, additional_files: Optional[List[str]] = []) -> AsyncIterable[WorkflowEvent]:
        pass
    
    @abstractmethod
    async def generate_content(self, message: str, additional_files: Optional[List[str]] = []) -> WorkflowRunResult:
        pass