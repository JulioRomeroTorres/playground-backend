from typing import List
from app.domain.utils import parrallel_pdf_to_img
from app.application.services.document_manager import DocumentManager
from fastapi import UploadFile

class HandleDocumentsUseCase:
    def __init__(self, document_manager: DocumentManager):
        self.document_manager = document_manager
        pass
    
    def process_file_by_content_type(self, file: UploadFile, local_file_path: str) -> List[str]:
        if file.content_type in ["application/pdf"]:
            return self.document_manager.process_document(local_file_path)
        return [local_file_path]

    async def upload_document(self, file: UploadFile) -> List[str]:
        local_file_path = await self.document_manager.save_document_locally(file)
        
        processed_files = self.process_file_by_content_type(file, local_file_path)
        return await self.document_manager.upload_to_bucket(processed_files)


        