import logging

from app.domain.repository.thread_manager_repository import IThreadManagerRepository

logger = logging.getLogger(__name__)


class ThreadManager:

    def __init__(
            self, 
            db_repository: IThreadManagerRepository
        ):
        self.db_repository = db_repository

    async def get_thread(self):
        await self.db_repository.get_thread()
        pass

    async def create_thread(self):
        await self.db_repository.create_thread()
        pass
    
