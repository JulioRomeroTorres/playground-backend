from abc import ABC, abstractmethod
from typing import Any, Optional, List, Dict
from app.domain.llm.llm_settings import LlmSettings
from agent_framework import ChatAgent

class IBaseAgentFactory(ABC):
    agent: ChatAgent

    @abstractmethod
    def get_agent_name(self) -> str:
        """Return the agent name for the ChatAgent.

        Returns:
            str: The name to be assigned to the ChatAgent instance.
        """
        pass

    @abstractmethod
    def get_agent_version(self) -> str:
        """Return the agent version for the ChatAgent.

        Returns:
            str: The version to be assigned to the ChatAgent instance.
        """
        pass

    @abstractmethod
    def get_tools(self) -> Optional[List[Any]]:
        """Return the tools for the ChatAgent.

        Returns:
            List[Any]: The tools to be assigned to the ChatAgent instance.
        """
        pass

    @abstractmethod
    def get_prompt_file(self) -> str:
        """Return the prompty file name (e.g., 'rag_agent.prompty').

        Returns:
            str: The prompty file name without path, located in infrastructure/prompts/.
        """
        pass
    
    @abstractmethod
    def get_system_instructions(self) -> str:
        pass
    
    @abstractmethod
    def create_agent(self, llm_setting: LlmSettings, session_id: str, thread_id: str, db_client: Any) -> ChatAgent:
        pass
        
    def __init__(self, llm_setting: LlmSettings, session_id: str, thread_id: str, db_client: Any) -> None:
        """Initialize the agent factory and create the agent.

        Args:
            chat_client: The chat client to use for agent creation.
        """
        self.agent = self.create_agent(llm_setting, session_id, thread_id, db_client)

class IAgentCore(ABC):
    @abstractmethod
    def create_agent(self, conversation_id: str) -> IBaseAgentFactory:
        pass

