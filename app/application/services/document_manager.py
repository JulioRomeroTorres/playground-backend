import shutil
from typing import List
from app.domain.repository.document_repository import IDocumentRepository
from app.domain.repository.storage_repository import IStorageRepository

class DocumentManager:
    def __init__(
                self,
                document_repository: IDocumentRepository,
                storage_repository: IStorageRepository                
                ) -> None:
        self.document_repository = document_repository
        self.storage_repository = storage_repository
        pass

    async def save_document_locally(self, file):
        return await self.document_repository.save_document_locally(file)

    def process_document(self, file_path: str) -> List[str]:
        processed_documents =  self.document_repository.process_document(file_path)
        print("Generated images files {processed_documents}")
        return processed_documents

    async def upload_to_bucket(self, list_files: str) -> List[str]:
        container_name = "ctnreu2aiasd02"
        files_urls = await self.storage_repository.upload_many_files(container_name, list_files)
        return files_urls