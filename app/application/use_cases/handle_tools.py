from typing import List, Any
from app.application.services.agent_information_manager import AgentInformationManager

class HandleToolsUseCase:
    def __init__(self, tool_manager: AgentInformationManager):
        self.tool_manager = tool_manager
        pass
    
    async def created_tool(self, user_id: str, tool_information: Any):
        all_tool_information = {"created_by": user_id, **tool_information.model_dump()}
        return await self.tool_manager.cre(all_tool_information)

    async def get_tools_by_user(self, tool_id: str) -> List[Any]:
        return await self.tool_manager.get_tools_by_user(tool_id)

    async def get_tool_by_user(self, tool_id: str) -> Any:
        return await self.tool_manager.get_specific_tool_by_user(tool_id)