from typing import Any
from app.domain.repository.item_sql_repository import IItemSqlRepository

class AgentInformationManager:
    def __init__(self, db_repository: IItemSqlRepository):
        self.db_repository = db_repository
        pass
    
    async def create_agent(self, agent_information: Any):
        collection_name = "agents_information"
        await self.db_repository.insert_item(agent_information, collection_name)
        agent = await self.db_repository.get_items_by_filter(
            filter={'agent_id': agent_information.get("agent_id")},
            projection={"name": 1, "model": 1, "description": 1 , "created_at": 1, "version": 1, "agent_id": 1}, 
            collection_name=collection_name,
            length=1
        )
        return agent

    async def create_tool(self, tool_information: Any):
        collection_name = "tools_information"

        await self.db_repository.insert_item(tool_information, collection_name)
        tool = await self.db_repository.get_items_by_filter(
            filter={'tool_id': tool_information.get("tool_id")},
            projection={"name": 1, "created_at": 1, "created_by": 1, "tool_id": 1, "alias": 1}, 
            collection_name=collection_name,
            length=1
        )
        return tool

    async def get_agents_by_user(self, user_id: str):
        return await self.db_repository.get_items_by_filter(
            filter={"created_by": user_id},
             projection={"name": 1, "description": 1,"model": 1, "agent_id": 1, "version": 1, "created_at": 1},
             collection_name="agents_information")
    
    async def get_agent_versions(self, agent_name): 
        return await self.db_repository.get_items_by_filter(
            filter={"name": agent_name},
             projection={"name": 1, "model": 1, "description": 1, "agent_id": 1, "version": 1, "created_at": 1},
             collection_name="agents_information")

    async def get_specific_agent_by_user(self, agent_id: str):
        agent_information = await self.db_repository.get_items_by_filter(
            filter={"agent_id": agent_id},
            collection_name="agents_information"
            )
        
        if len(agent_information) < 1:
            return None
        
        selected_agent = agent_information[0] 
        tools_ids = selected_agent.get("tools_ids", [])
        selected_agent["tools"] = []
        if len(tools_ids) > 0:
            tools_information = await self.db_repository.get_items_by_filter(
            filter={"tool_id": { "$in": tools_ids }},
            collection_name="tools_information"
            )
            selected_agent["tools"] = tools_information
        return selected_agent
            
    async def get_tools_by_user(self, user_id: str):
        return await self.db_repository.get_items_by_filter(
            filter={"created_by": user_id},
            projection={"name": 1, "description": 1, "created_at": 1, "tool_id": 1, "alias": 1},
            collection_name="tools_information"
        )

    async def get_specific_tool_by_user(self, tool_id: str):
        selected_tool = await self.db_repository.get_items_by_filter(
            filter={"tool_id": tool_id},
            collection_name="tools_information"
        )
        return selected_tool[0]
        