from typing import Any
from app.domain.agent_core.service import IAgentCore, IBaseAgentFactory
from app.infrastructure.agents.drafting_agent import DraftingAgent

class AgentCore(IAgentCore):
    def __init__(self, db_client: Any, storage_repository: Any):
        self.db_client = db_client
        self.storage_repository = storage_repository
        pass
    
    def create_agent(self, conversation_id: str) -> IBaseAgentFactory:
        return DraftingAgent(conversation_id, self.db_client, self.storage_repository)