from typing import (
    Any, AsyncGenerator, Optional,
    List, Dict, Any
)

from app.domain.agent import AgentResponse
from app.domain.agent.agent import ConversationResponse

from app.domain.agent_core.service import IAgentCore
from app.application.services.thread_manager import ThreadManager
from app.domain.agent.agent import AgentSettings

from app.application.services.agent_information_manager import AgentInformationManager

from app.domain.conversation.conversation import (
    StartStreamingResponse, DataStreamingResponse, EndStreamingResponse,
    TypeStreamingResponseEnum  
) 

from app.domain.utils import generate_uuid, get_current_datetime

class MessageUseCase:
    def __init__(
        self,
        agent_core: IAgentCore,
        agent_information_manager: AgentInformationManager
        ):
        self.agent_core = agent_core
        self.agent_information_manager = agent_information_manager
        pass

    async def create_thread(self, conversation_id: str) -> None:
        raw_agent_settings = await self.agent_information_manager.get_specific_agent_by_user()
        agent_settings = AgentSettings(**raw_agent_settings)
        self.agent_core.create_agent(conversation_id, agent_settings)
    
class HandleMessageUseCase(MessageUseCase):
    def __init__(
        self,
        agent_information_manager: AgentInformationManager,
        agent_core: IAgentCore
    ):
        super().__init__(agent_core, agent_information_manager)

    async def execute(
        self,
        conversation_id: str,
        message: str,
        agent_id: str,
        additional_files: Optional[List[str]] = [],
        decision: Optional[str] = None,
    ) -> AgentResponse:

        await self.create_thread(conversation_id)

        agent_response = await self.agent_core.generate_content(
            message=message,
            additional_files=additional_files,
            agent_id=agent_id
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
        agent_information_manager: AgentInformationManager,
        agent_core: IAgentCore
    ):
        super().__init__(agent_core, agent_information_manager)

    async def execute(
        self,
        conversation_id: str,
        message: str,
        agent_id: str,
        additional_files: Optional[List[str]] = [],
        decision: Optional[str] = None
    ) -> AsyncGenerator[dict[str, Any], None]:
        
        await self.create_thread(conversation_id)

        yield StartStreamingResponse(agent=self.agent_core.agent_name).model_dump()

        async for chunk in self.agent_core.generate_stream_content(
            message=message,
            additional_files=additional_files
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