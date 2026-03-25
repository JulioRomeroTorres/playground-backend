import asyncio
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

from app.domain.agent.workflow import CompletedWorkflowInformation

from app.domain.orchestrator.service import IWorkflowOrchestrator

from app.domain.utils import generate_uuid, get_current_datetime
from agent_framework import (
    WorkflowRunResult, AgentRunResponse
)

class MessageUseCase:
    def __init__(
        self,
        agent_core: IAgentCore,
        agent_information_manager: AgentInformationManager
        ):
        self.agent_core = agent_core
        self.agent_information_manager = agent_information_manager
        self.agent_name = None
        self.model = None
        pass

    async def create_thread(self, agent_id: str, conversation_id: str) -> None:
        raw_agent_settings = await self.agent_information_manager.get_specific_agent_by_user(agent_id)
        agent_settings = AgentSettings(**raw_agent_settings)
        self.agent_name = agent_settings.name
        self.model = agent_settings.model
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

        await self.create_thread(agent_id, conversation_id)

        agent_response = await self.agent_core.generate_content(
            message=message,
            additional_files=additional_files
            )

        return AgentResponse(
            message=agent_response.messages[-1].text,
            agent_name=self.agent_name,
            model_name=self.model,
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
        
        await self.create_thread(agent_id, conversation_id)

        yield StartStreamingResponse(agent=self.agent_name).model_dump()

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

class HandleWorkflowMessageUseCase:
    def __init__(
        self,
        workflow_information_manager: AgentInformationManager,
        workflow_orchestrator: IWorkflowOrchestrator
    ):
        self.workflow_information_manager = workflow_information_manager
        self.workflow_orchestrator = workflow_orchestrator

    async def execute(self, 
        conversation_id: str,
        message: str,
        workflow_id: str,
        additional_files: Optional[List[str]] = [],
        decision: Optional[str] = None
    ) -> WorkflowRunResult:
        workflow_structure = await self.workflow_information_manager.get_specific_workflow_information(workflow_id)
        workflow_structure = CompletedWorkflowInformation(**workflow_structure)

        agents_coroutine_information = [
            self.workflow_information_manager.get_specific_agent_by_user(agent_id)
            for agent_id in workflow_structure.unique_agents_ids
        ]
        
        agents_information = await asyncio.gather(*agents_coroutine_information)

        [
            self.workflow_orchestrator.create_agent(
                AgentSettings(
                    **{
                        "id": agent_information["agent_id"],
                        "name":agent_information["name"],
                        "version":agent_information["version"],
                        "system_instruction": agent_information["system_instruction"],
                        "model":agent_information["model"],
                        "tools":agent_information["tools"]
                    }
                )
            )
            for agent_information in  agents_information
        ]

        self.workflow_orchestrator.build_workflow(workflow_structure)

        workflow_response = await self.workflow_orchestrator.generate_content(message)

        return workflow_response