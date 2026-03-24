from abc import ABC, abstractmethod
from typing import Any, AsyncGenerator, TYPE_CHECKING, Optional
from app.domain.agent.agent import AgentSettings

if TYPE_CHECKING:
    from app.domain.agent import AgentResponse

class IWorkflowOrchestrator(ABC):

    @abstractmethod
    def create_agent(agent_settings: AgentSettings, conversation_id: Optional[str] = None) -> None:
        pass

    @abstractmethod
    def build_workflow(self, workflow_structure: Any) -> None:
        pass

    @abstractmethod
    async def process_message(
        self,
        message: str,
        session_id: str,
        context: Any | None = None,
        messages: list[Any] | None = None,
        session_state: dict[str, Any] | None = None,
        decision: Optional[str] = None
    ) -> "AgentResponse":
        pass

    @abstractmethod
    async def process_message_stream(
        self,
        message: str,
        session_id: str,
        context: Any | None = None,
        messages: list[Any] | None = None,
        session_state: dict[str, Any] | None = None,
        decision: Optional[str] = None
    ) -> AsyncGenerator[dict[str, Any], None]:
        pass
