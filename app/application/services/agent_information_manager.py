from typing import Any
from app.domain.repository.item_sql_repository import IItemSqlRepository

class AgentInformationManager:
    def __init__(self, db_repository: IItemSqlRepository):
        self.db_repository = db_repository
        pass
    
    async def create_agent(self, agent_information: Any):
        collection_name = "agents_information"
        return await self.db_repository.insert_item(agent_information, collection_name)

    async def create_tool(self, tool_information: Any):
        collection_name = "tools_information"
        return await self.db_repository.insert_item(tool_information, collection_name)

    async def get_agents_by_user(self, user_id: str):
        return await self.db_repository.get_items_by_filter(
            filter={"created_by": user_id},
             projection={"name": 1, "description": 1, "version": 1, "created_at": 1},
             collection_name="agents_information")
        
    async def get_specific_agent_by_user(self, agent_id: str):
        agent_information = await self.db_repository.get_items_by_filter(
            filter={"agent_id": agent_id},
            collection_name="agents_information"
            )

        tools_ids = agent_information.get("tools_ids", [])

        if len(tools_ids) > 0:
            agent_information = await self.db_repository.get_items_by_filter(
            filter={"tool_id": { "$in": tools_ids }},
            collection_name="tools_information"
            )
            
    async def get_tools_by_user(self, user_id: str):
        return await self.db_repository.get_items_by_filter(
            filter={"created_by": user_id},
            projection={"name": 1, "description": 1, "created_at": 1},
            collection_name="tools_information"
        )

    async def get_specific_tool_by_user(self, tool_id: str):
        return await self.db_repository.get_items_by_filter(
            filter={"tool_id": tool_id},
            collection_name="tools_information"
        )
        