from typing import List, Any
from app.domain.repository.item_sql_repository import IItemSqlRepository
from app.domain.repository.thread_manager_repository import IThreadManagerRepository
from app.domain.utils import get_or_create_uuid

class ThreadManagerRepository(IThreadManagerRepository):
    def __init__(
        self,
        db_repository: IItemSqlRepository
    ) -> None:
        self.db_repository = db_repository
    
    async def create_thread(self, session_id: str, agents_names: List[str]) -> List[Any]:
        agents_sessions_threads = [ { "name": agent_name, "id":  str(get_or_create_uuid()) }  for agent_name in agents_names]
        await self.db_repository.insert_item({"session_id": session_id, "threads": agents_sessions_threads}, "threads_manager")
    
    async def get_threads(filters: Any) -> List[Any]:
        pass