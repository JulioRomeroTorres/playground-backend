import logging
from typing import List, Any, Dict, Coroutine, Optional, AsyncIterable
from app.domain.repository.item_sql_repository import IItemSqlRepository

from app.domain.repository.content_safety_repository import IContentSafetyRepository
from app.domain.agent_core.service import IAgentCore, IBaseAgentFactory

from app.domain.contants import DecisionAction
from app.domain.exceptions import ThreadNotFound, GuardialError
from app.domain.utils import get_metadata_from_uri

from agent_framework import (
    ChatAgent, AgentRunResponse, AgentRunResponseUpdate,
    UriContent, TextContent, BaseContent, ChatMessage, DataContent
    )

logger = logging.getLogger(__name__)

class AgentManager:
    def __init__(
                self,
                agent_core: IAgentCore,
                content_safety_repository: IContentSafetyRepository
                ) -> None:
        self.content_safety_repository = content_safety_repository
        self.agent_core =  agent_core
        self.agent_factory:IBaseAgentFactory = None
        self.agent_name = None

    def create_thread(self, conversation_id: str):
        self.agent_factory = self.agent_core.create_agent(conversation_id)
        self.agent_name = self.agent_factory.get_agent_name()

    def create_uri_content(self, metadata: Dict[str, str]):
        return UriContent(uri=metadata.get('uri'), media_type=metadata.get('media_type'))
    
    def create_additional_information_content(self, additional_information: Optional[Dict[str, Any]] = dict()) -> List[Any]:
        return [
                TextContent(text=f"Esta es la URL del documento plantilla o template {additional_information.get("reference_document")}")
            ]

    def prepare_content(
                    self, message: str, additional_files: Optional[List[str]] = [], 
                    additional_information:Optional[Dict[str, Any]] = dict()) -> ChatMessage:
        
        additional_content_files = [
            self.create_uri_content(get_metadata_from_uri(additional_file))
            for additional_file in additional_files
        ]

        additional_content_information = self.create_additional_information_content(additional_information)

        return ChatMessage(
            role="user",
            contents=[ TextContent(text=message) ,*additional_content_files, *additional_content_information]
        ) 

    async def generate_stream_content(self, message: str, additional_files: Optional[List[str]] = [], 
                                      additional_information:Optional[Dict[str, Any]] = dict()) -> AsyncIterable[AgentRunResponseUpdate]:
        content = self.prepare_content(message, additional_files, additional_information)
        async for event in self.agent_factory.agent.run_stream(content):
            print("UJUU", event)
            yield event
    
    async def generate_content(self, message: str, additional_files: Optional[List[str]] = [], additional_information:Optional[Dict[str, Any]] = dict()) -> AgentRunResponse:
        content = self.prepare_content(message, additional_files, additional_information)
        agent_response = await self.agent_factory.agent.run(content)
        return agent_response
    
    async def apply_guardial(self, message: str, reject_thresholds: Dict[str, Any], blocklist_names: Optional[List[str]] = []) -> None:
        analysis_result = await self.content_safety_repository.analyze_text(message, blocklist_names)
        decision, thresholds_results = self.content_safety_repository.make_decision(analysis_result, reject_thresholds)

        print(f"Content Safety Analysis -> Decicion: {decision} results: {thresholds_results}")

        if decision == DecisionAction.REJECT:
            raise GuardialError(message, thresholds_results)
        
