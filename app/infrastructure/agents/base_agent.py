import time
import logging
from abc import ABC, abstractmethod
from typing import Any, List, Optional
from agent_framework import ChatAgent
from app.domain.llm.llm_settings import LlmSettings
from app.domain.agent.telemetry import TelemetryProperties
from app.domain.contants import TypeDeploymentClient
from agent_framework.azure import AzureOpenAIChatClient, AzureAIClient
from agent_framework.openai import OpenAIChatClient
from azure.identity import DefaultAzureCredential
from azure.ai.projects.aio import AIProjectClient
from app.infrastructure.repository.mongo_db import MongoDbRepository
from app.infrastructure.repository.mongo_message_store import MongoChatMessageStore
from app.infrastructure.agents.plugins.monitored_agent import MonitoredChatAgent
from app.infrastructure.agents.clients.external_client import ExternalClient
from agent_framework import Middleware
    
class BaseAgentFactory(ABC):
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
    def get_middleware(self) -> Optional[List[Middleware]]:
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
    
    def ai_foundry_agent(self, llm_setting: LlmSettings, conversation_id: str, chat_message_store_factory: Any) -> ChatAgent:
        project_client = AIProjectClient(
            endpoint=llm_setting.endpoint, 
            credential=DefaultAzureCredential()
        )

        azure_client = AzureAIClient(
            project_client=project_client,
            agent_name=self.get_agent_name(),
            agent_version=self.get_agent_version(),
            model_deployment_name=llm_setting.model
        )

        return ChatAgent(
            chat_client=azure_client,
            name=self.get_agent_name(),
            conversation_id=conversation_id
        )
    
    def external_ai_foundry_agent(self, llm_setting: LlmSettings, conversation_id: str, chat_message_store_factory: Any) -> ChatAgent:
        client = ExternalClient(
            base_url=llm_setting.endpoint,
            conversation_id=conversation_id
        )

        return ChatAgent(
            chat_client=client,
            name=self.get_agent_name(),
            conversation_id=conversation_id
        )
    
    def agent_framework_agent(self, llm_setting: LlmSettings, conversation_id: str, chat_message_store_factory: Any) -> MonitoredChatAgent:
        agent_name = self.get_agent_name()
        chat_client = AzureOpenAIChatClient(
            endpoint=llm_setting.endpoint,
            api_key=llm_setting.api_key,
            deployment_name=llm_setting.model,
            api_version=llm_setting.version
        )

        return MonitoredChatAgent(
            chat_client=chat_client,
            name=self.get_agent_name(),
            instructions=self.get_system_instructions(),
            temperature=llm_setting.temperature,
            top_p=llm_setting.top_p,
            tools=self.get_tools(),
            chat_message_store_factory= None if conversation_id is None else lambda: chat_message_store_factory,
            telemetry_properties=TelemetryProperties(
                **{
                    "agent.id": agent_name,
                    "agent.name": agent_name,
                    "request.model": f"{llm_setting.model}-{llm_setting.version}",
                    "agent.conversation.id": conversation_id
                }
            ),
            middleware=self.get_middleware()
        )


    def create_agent(self, llm_setting: LlmSettings, session_id: str, thread_id: str, db_client: Any) -> ChatAgent:
    
        chat_message_store_factory = None if thread_id is None else MongoChatMessageStore( 
                                db_repository=MongoDbRepository(
                                    database_name="agent_manager",
                                    collection_name="conversations",
                                    client=db_client
                                ),
                                thread_id=thread_id
                            )
        MAPPER_REGISTER_AGENT_TYPE = {
            TypeDeploymentClient.AGENT_FRAMEWORK: self.agent_framework_agent,
            TypeDeploymentClient.AI_FOUNRY: self.ai_foundry_agent,
            TypeDeploymentClient.EXTERNAL_AI_FOUNDRY: self.external_ai_foundry_agent
        }

        return MAPPER_REGISTER_AGENT_TYPE.get(llm_setting.deployment_type)(
            llm_setting,
            thread_id,
            chat_message_store_factory
        )

    def __init__(self, llm_setting: LlmSettings, session_id: str, thread_id: str, db_client: Any) -> None:
        """Initialize the agent factory and create the agent.

        Args:
            chat_client: The chat client to use for agent creation.
        """
        self.agent = self.create_agent(llm_setting, session_id, thread_id, db_client)
