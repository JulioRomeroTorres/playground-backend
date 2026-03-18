from abc import ABC, abstractmethod
from typing import Any, AsyncGenerator, TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from app.domain.agent import AgentResponse

class Orchestrator(ABC):

    @abstractmethod
    def create_workflow(
        self,
    ) -> Any:
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
