from typing import Any, List, Optional
from app.infrastructure.agents.base_agent import BaseAgentFactory
from app.domain.llm.llm_settings import LlmSettings

from app.infrastructure.tools.file_manager import (
    get_template_document, extract_document_structure
)
from app.infrastructure.tools.file_manager import (
    FillDocumentTool
)
from app.infrastructure.prompt_manager import get_prompt_manager
from app.config import get_settings
from agent_framework import Middleware
from maf_telemetry.guardrails.middleware import get_guardrails

class DraftingAgent(BaseAgentFactory):

    def get_agent_name(self) -> str:
        return self.agent_name

    def get_agent_version(self) -> str:
        return self.agent_version
    
    def get_system_instructions(self) -> str:
        return self.system_instructions

    def get_prompt_file(self) -> None:
        return "drafting_agent.prompty"

    def get_tools(self) -> Optional[List[Any]]:
        return [
            get_template_document, FillDocumentTool(self.storage_repository).execute, extract_document_structure
        ]
    
    def get_middleware(self) -> Optional[List[Middleware]]:
        return get_guardrails(["grl_health_and_wellness_4_levels_001"])

    def __init__(self, conversation_id:str, db_client: Any = None, storage_repository: Any = None):
        
        prompt_manager = get_prompt_manager()
        settings = get_settings()

        self.agent_name = "drafting-agent"
        self.agent_version = settings.agent_version
        self.storage_repository = storage_repository
        self.system_instructions = prompt_manager.render_instructions(self.get_prompt_file())
        
        self.llm_settings = LlmSettings(
            version=settings.azure_openai_api_version,
            endpoint=settings.azure_openai_endpoint,
            api_key=settings.azure_openai_api_key,
            model=settings.azure_openai_deployment,
        )

        super().__init__(self.llm_settings, "", conversation_id, db_client)