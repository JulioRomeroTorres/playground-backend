from typing import List, Any
from app.application.services.agent_information_manager import AgentInformationManager

class HandleAgentsUseCase:
    
    def __init__(self, agent_information_manager: AgentInformationManager):
        self.agent_information_manager = agent_information_manager
        pass

    async def create_agent(self, user_id: str, agent_information: Any):
        all_agent_information = {"created_by": user_id, **agent_information.model_dump()}
        return await self.agent_information_manager.create_agent(all_agent_information)

    async def get_agents_by_user(self, user_id: str) -> List[Any]:
        return await self.agent_information_manager.get_agents_by_user(user_id)

    async def get_agent_by_user(self, agent_id: str) -> Any:
        return await self.agent_information_manager.get_specific_agent_by_user(agent_id)

         