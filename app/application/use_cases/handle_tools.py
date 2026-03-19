from typing import List, Any
from app.application.services.agent_information_manager import AgentInformationManager
from app.domain.utils import generate_uuid, get_datetime_now
from app.domain.agent.tools import (
    SimplifyToolInformation,
    CompletedToolInformation
)

class HandleToolsUseCase:
    def __init__(self, tool_manager: AgentInformationManager):
        self.tool_manager = tool_manager
        pass
    
    async def create_tool(self, user_id: str, tool_information: Any) -> SimplifyToolInformation:
        all_agent_information = {
            "created_by": user_id, 
            "tool_id": f"{generate_uuid()}" , 
            "created_at": get_datetime_now(),
            **tool_information.model_dump()
            }
        created_register = await self.tool_manager.create_tool(all_agent_information)
        
        if len(created_register) < 1:
            print("Error al encontrar el agente")

        print("register", created_register[0])

        return SimplifyToolInformation(**created_register[0])

    async def get_tools_by_user(self, tool_id: str) -> List[SimplifyToolInformation]:
        selected_tools = await self.tool_manager.get_tools_by_user(tool_id)
        return [ SimplifyToolInformation(**tool)  for tool in selected_tools ]

    async def get_tool_by_user(self, tool_id: str) -> CompletedToolInformation:
        selected_tool = await self.tool_manager.get_specific_tool_by_user(tool_id)
        return CompletedToolInformation(**selected_tool)