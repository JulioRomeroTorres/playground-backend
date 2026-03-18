from abc import ABC, abstractmethod
from typing import Any, List, Dict, Optional

class IFileDocumentRepository(ABC):

    @abstractmethod
    def analize_placeholders(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def refill_document(self, fill_data: Dict[str, Any], output_path: Optional[str] = 'tmp/output.pptx') -> None:
        pass