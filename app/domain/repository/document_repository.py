from abc import ABC, abstractmethod
from typing import Any, List

class IDocumentRepository(ABC):

    @abstractmethod
    async def save_document_locally(self, file: Any) -> str:
        pass

    @abstractmethod
    async def process_document(self, local_file_path: str) -> List[str]:
        pass