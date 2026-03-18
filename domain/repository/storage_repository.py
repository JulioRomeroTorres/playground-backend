from typing import List, Optional
from abc import ABC, abstractmethod

class IStorageRepository(ABC):

    @abstractmethod
    async def upload_file(self, container_name: str, local_file_path: str, blob_name: Optional[str]) -> str:
        pass

    @abstractmethod
    async def upload_many_files(self, container_name: str, files_list: List[str], max_concurrent: Optional[str] = 20 ) -> List[str]:
        pass