from abc import ABC, abstractmethod
from typing import List, Any

class IThreadManagerRepository(ABC):
    @abstractmethod
    async def create_thread() -> List[Any]:
        pass

    @abstractmethod
    async def get_threads(filters: Any) -> List[Any]:
        pass
