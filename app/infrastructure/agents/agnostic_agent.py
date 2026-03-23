from typing import Any, List, Optional
from app.domain.agent.tools import ToolSettings
from app.infrastructure.agents.base_agent import BaseAgentFactory
from app.infrastructure.tools.tool_factory import DynamicToolFactory
from app.domain.llm.llm_settings import LlmSettings
from app.domain.agent.agent import AgentSettings

from app.config import get_settings
from agent_framework import Middleware

MAPPER_VERSION = {
    "gpt-4o-mini": "2025-01-01-preview",
    "gpt-4": "2025-01-01-preview",
}

class AgnosticAgent(BaseAgentFactory):

    def get_agent_name(self) -> str:
        return self.agent_name

    def get_agent_version(self) -> str:
        return self.agent_version
    
    def get_system_instructions(self) -> str:
        return self.system_instructions

    def get_prompt_file(self) -> None:
        return None

    def get_tools(self) -> Optional[List[Any]]:
        tools = []
        for tool_info in self.tools_information:
            tool_setting = ToolSettings(**{
                "name": tool_info.name,
                "description": tool_info.description,
                "logical_content": tool_info.logic_content,
                "input_parameters": tool_info.input_params
            })
            tool = DynamicToolFactory.create_tool(tool_setting)
            tools.append(tool)
        
        return None if len(tools) < 1 else tools
    
    def get_middleware(self) -> Optional[List[Middleware]]:
        return None

    def __init__(self, conversation_id: str, agent_metadata: AgentSettings, db_client: Any = None):
        
        settings = get_settings()
        print("Agent Metadata", agent_metadata)
        self.agent_name = agent_metadata.name
        self.agent_version = agent_metadata.version

        self.system_instructions = agent_metadata.system_instruction
        
        model_name = agent_metadata.model
        model_version= MAPPER_VERSION[model_name]

        self.tools_information = agent_metadata.tools

        self.llm_settings = LlmSettings(
            version=model_version,
            endpoint=settings.azure_openai_endpoint,
            api_key=settings.azure_openai_api_key,
            model=model_name,
        )

        super().__init__(self.llm_settings, "", conversation_id, db_client)