import logging
from typing import List, Any, Dict, Coroutine, Optional, AsyncIterable
from app.domain.repository.item_sql_repository import IItemSqlRepository

from app.domain.repository.content_safety_repository import IContentSafetyRepository
from app.domain.agent_core.service import IAgentCore, IBaseAgentFactory

from app.domain.contants import DecisionAction
from app.domain.exceptions import ThreadNotFound, GuardialError
from app.domain.utils import get_metadata_from_uri
from app.domain.agent.agent import AgentSettings

from agent_framework import (
    ChatAgent, AgentRunResponse, AgentRunResponseUpdate,
    UriContent, TextContent, BaseContent, ChatMessage, DataContent
    )

from app.infrastructure.agents.agnostic_agent import AgnosticAgent

logger = logging.getLogger(__name__)

class AgentCore(IAgentCore):
    def __init__(
                self,
                db_client: Any,
                content_safety_repository: IContentSafetyRepository
                ) -> None:

        self.content_safety_repository = content_safety_repository
        self.agent_factory:IBaseAgentFactory = None
        self.db_client = db_client
        self.agent_name = None

    def create_agent(self, conversation_id: str, agent_settings: AgentSettings) -> None:
        self.agent_factory = AgnosticAgent(conversation_id, agent_settings, self.db_client)
        self.agent_name = agent_settings.name

    def create_uri_content(self, metadata: Dict[str, str]):
        return UriContent(uri=metadata.get('uri'), media_type=metadata.get('media_type'))

    def prepare_content(
                    self, message: str, additional_files: Optional[List[str]] = []
                    ) -> ChatMessage:
        
        additional_content_files = [
            self.create_uri_content(get_metadata_from_uri(additional_file))
            for additional_file in additional_files
        ]

        return ChatMessage(
            role="user",
            contents=[ TextContent(text=message) ,*additional_content_files]
        ) 

    async def generate_stream_content(self, message: str, additional_files: Optional[List[str]] = []) -> AsyncIterable[AgentRunResponseUpdate]:
        content = self.prepare_content(message, additional_files)
        async for event in self.agent_factory.agent.run_stream(content):
            yield event
    
    async def generate_content(self, message: str, additional_files: Optional[List[str]] = []) -> AgentRunResponse:
        content = self.prepare_content(message, additional_files)
        agent_response = await self.agent_factory.agent.run(content)
        return agent_response
    
    async def apply_guardial(self, message: str, reject_thresholds: Dict[str, Any], blocklist_names: Optional[List[str]] = []) -> None:
        analysis_result = await self.content_safety_repository.analyze_text(message, blocklist_names)
        decision, thresholds_results = self.content_safety_repository.make_decision(analysis_result, reject_thresholds)

        print(f"Content Safety Analysis -> Decicion: {decision} results: {thresholds_results}")

        if decision == DecisionAction.REJECT:
            raise GuardialError(message, thresholds_results)
        
