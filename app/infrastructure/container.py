from typing import Any
from functools import lru_cache
from app.config import get_settings

from app.infrastructure.agent_core import AgentCore
from app.application.services.thread_manager import ThreadManager
from app.application.services.document_manager import DocumentManager

from app.application.use_cases.handle_conversation import (
    HandleMessageUseCase, HandleMessageStreamUseCase, 
    HandleThreadsUseCase
)

from app.application.use_cases.handle_document import (
    HandleDocumentsUseCase
)

from app.application.use_cases.handle_agents import (
    HandleAgentsUseCase
)

from app.application.use_cases.handle_tools import (
    HandleToolsUseCase
)

from app.infrastructure.client_factory import ChatClientFactory
from app.infrastructure.orchestrator import WorkflowOrchestrator

from app.infrastructure.repository.mongo_db import MongoDbRepository
from app.infrastructure.repository.thread_manager import ThreadManagerRepository
from app.infrastructure.agent_core import AgentCore

from app.infrastructure.repository.content_safety import ContentSafetyGuardilRepository

from app.infrastructure.repository.document_manager import DocumentManagerRepository
from app.infrastructure.repository.storage_account import StorageAccountRepository

from pymongo import AsyncMongoClient
from app.infrastructure.managers.http_manager import HttpRepositoryManager
from app.application.services.agent_information_manager import AgentInformationManager
from azure.ai.contentsafety.aio import ContentSafetyClient
from azure.core.credentials import AzureKeyCredential

from azure.identity.aio import DefaultAzureCredential
from azure.storage.blob.aio import BlobServiceClient

class DependencyContainer:
    def __init__(self):
        self._instances = {}
        self._factories = {}
        self._initialized = False
        self._db_client = None
        self._storage_client = None
        self._content_safety_client = None

    def _ensure_initialized(self):
        if self._initialized:
            return

        settings = get_settings()
        # Core infrastructure
        self._factories["chat_client"] = ChatClientFactory.create_client
        
        self._factories["db_repository"] = lambda: MongoDbRepository(self._get_db_client(), settings.mongo_db_name)        
        self._factories["thread_manager_repository"] = lambda: ThreadManagerRepository(self.get("db_repository"))

        self._factories["content_safety_repository"] = lambda: ContentSafetyGuardilRepository(self._get_content_safety_client())
        
        #TODO: replace this part
        self._factories["document_repository"] = lambda: DocumentManagerRepository()
        self._factories["storage_repository"] = lambda: StorageAccountRepository(self._get_storage_client(), settings.storage_account_name)

        self._factories["agent_information_manager"] = lambda: AgentInformationManager(
            self.get('db_repository')
        )

        self._factories["tool_manager"] = lambda: AgentInformationManager(
            self.get('db_repository')
        )

        self._factories["agent_manager"] = lambda: AgentCore(
            self._get_db_client(),
            self.get('content_safety_repository'),
        )
        self._factories["thread_manager"] = lambda: ThreadManager(
            self.get('thread_manager_repository')
        )

        self._factories["document_manager"] = lambda: DocumentManager(
                self.get('document_repository'),
                self.get('storage_repository')
            )

        self._factories["agent_core"] = lambda: AgentCore(self._get_db_client(), self.get('content_safety_repository'))

        # Orchestrator (depends on chat_client and conversation_manager)
        self._factories["orchestrator"] = lambda: WorkflowOrchestrator(
            self.get("conversation_manager"),
            self._get_db_client()
        )

        self._initialized = True

    def get(self, service_name: str) -> Any:
        self._ensure_initialized()

        if service_name not in self._instances:
            if service_name not in self._factories:
                raise ValueError(f"Unknown service: {service_name}")
            self._instances[service_name] = self._factories[service_name]()

        return self._instances[service_name]

    def get_handle_message_use_case(self) -> HandleMessageUseCase:
        return HandleMessageUseCase(
            agent_core=self.get("agent_core")
        )

    def get_handle_message_stream_use_case(self) -> HandleMessageStreamUseCase:
          return HandleMessageStreamUseCase(
            agent_information_manager=self.get("agent_information_manager"),
            agent_core=self.get("agent_core")
        )

    def get_handle_threads_use_case(self) -> HandleThreadsUseCase:
          return HandleThreadsUseCase(
            agent_information_manager=self.get("agent_information_manager"),
            thread_manager=self.get("thread_manager")
        )

    def get_handle_documents_use_case(self) -> HandleDocumentsUseCase:
        return HandleDocumentsUseCase(
            document_manager=self.get("document_manager")
        )
    
    def get_handle_agents_use_case(self) -> HandleAgentsUseCase:
        return HandleAgentsUseCase(
            agent_information_manager=self.get("agent_information_manager")
        )
    
    def get_handle_tools_use_case(self) -> HandleToolsUseCase:
        return HandleToolsUseCase(
            tool_manager=self.get("tool_manager")
        )

    def clear(self):
        self._instances.clear()
        self._initialized = False
    
    def _get_db_client(self) -> AsyncMongoClient:
        if self._db_client is None:
            settings = get_settings()
            self._db_client = AsyncMongoClient(settings.mongo_db_connection_string)
        return self._db_client

    def _get_storage_client(self) -> BlobServiceClient:
        if self._storage_client is None:
            settings = get_settings()
            credential = DefaultAzureCredential()
            self._storage_client = BlobServiceClient(settings.storage_account_url, credential=credential)
        return self._storage_client

    def _get_content_safety_client(self) -> AsyncMongoClient:
        if self._content_safety_client is None:
            settings = get_settings()
            self._content_safety_client = ContentSafetyClient(
                settings.content_safety_endpoint,
                AzureKeyCredential(settings.content_safety_api_key)
            )
            
        return self._content_safety_client

    async def close_all(self):
        
        print("Closing all connection...")
        if self._db_client:
            await self._db_client.close()
        
        if self._content_safety_client:
            await self._content_safety_client.close()

        await HttpRepositoryManager.close_all_sessions()

        self.clear()
        print("All connection are closed")


    def get_session_count(self) -> int:
        if "conversation_manager" in self._instances:
            return len(self._instances["conversation_manager"].conversations)
        return 0


@lru_cache
def get_container() -> DependencyContainer:
    return DependencyContainer()
