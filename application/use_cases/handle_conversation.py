from typing import (
    Any, AsyncGenerator, Optional,
    List, Dict, Any
)

from app.domain.agent import AgentResponse
from app.domain.agent.agent import ConversationResponse

from app.application.services.agent_manager import AgentManager
from app.application.services.thread_manager import ThreadManager

from app.domain.conversation.conversation import (
    StartStreamingResponse, DataStreamingResponse, EndStreamingResponse,
    TypeStreamingResponseEnum  
) 

from app.domain.utils import generate_uuid, get_current_datetime

class MessageUseCase:
    def __init__(
        self,
        agent_manager: AgentManager
        ):
        self.agent_manager = agent_manager
        pass

    def create_thread(self, conversation_id: str) -> None:
        self.agent_manager.create_thread(conversation_id)
    
class HandleMessageUseCase(MessageUseCase):
    def __init__(
        self,
        agent_manager: AgentManager
    ):
        super().__init__(agent_manager)

    async def execute(
        self,
        conversation_id: str,
        message: str,
        additional_files: Optional[List[str]] = [],
        decision: Optional[str] = None,
        additional_information: Optional[Dict[str, Any]] = dict(),
        trace: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:

        self.create_thread(conversation_id)

        agent_response = await self.agent_manager.generate_content(
            message=message,
            additional_files=additional_files,
            additional_information=additional_information
            )

        return AgentResponse(
            message=agent_response.messages[-1].text,
            agent_name=self.agent_manager.agent_name,
            metadata={
                "conversation_id": conversation_id,
                "usage_tokens": 100,
                "message_id": ""
            }
        )

class HandleMessageStreamUseCase(MessageUseCase):
    def __init__(
        self,
        agent_manager: AgentManager
    ):
        super().__init__(agent_manager)

    async def execute(
        self,
        conversation_id: str,
        message: str,
        additional_files: Optional[List[str]] = [],
        decision: Optional[str] = None,
        additional_information: Optional[Dict[str, Any]] = dict(),
        trace: Optional[Dict[str, Any]] = None
    ) -> AsyncGenerator[dict[str, Any], None]:
        
        self.create_thread(conversation_id)

        yield StartStreamingResponse(agent=self.agent_manager.agent_name).model_dump()

        async for chunk in self.agent_manager.generate_stream_content(
            message=message,
            additional_files=additional_files,
            additional_information=additional_information
        ):
            yield DataStreamingResponse(type=TypeStreamingResponseEnum.DATA.value, text=chunk.text).model_dump()

        yield EndStreamingResponse(type=TypeStreamingResponseEnum.END.value).model_dump()

class HandleThreadsUseCase():
    def __init__(
        self,
        thread_manager: ThreadManager,
    ):
        self.thread_manager = thread_manager

    async def create(
        self
    ) -> ConversationResponse:
        return ConversationResponse(
            conversation_id=f"conv_{generate_uuid()}",
            created_at=f"{get_current_datetime()}"
        )

    async def get(
        self,
        filters
    ) -> None:
        return 