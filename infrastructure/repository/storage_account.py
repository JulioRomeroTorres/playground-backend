import os
import logging
from typing import Optional, Any, List
from datetime import datetime, timedelta, timezone
from azure.storage.blob.aio import BlobServiceClient
from azure.storage.blob import generate_blob_sas, BlobSasPermissions
from app.domain.repository.storage_repository import IStorageRepository
from app.domain.utils import get_class_name 
from concurrent.futures import as_completed, ThreadPoolExecutor
from tqdm import tqdm 
import asyncio

class StorageAccountRepository(IStorageRepository):
    def __init__(self, client: BlobServiceClient, storage_account: str):
        self.client = client
        self.storage_account = storage_account
        self.logger = logging.getLogger(get_class_name(self))
        pass
    
    async def generate_token(self, container_name: str, blob_name: str) -> str:
        user_delegation_key = await self.client.get_user_delegation_key(
            key_start_time=datetime.now(timezone.utc) - timedelta(minutes=2),
            key_expiry_time=datetime.now(timezone.utc) + timedelta(hours=1))

        return generate_blob_sas(
            account_name=self.storage_account,
            container_name=container_name,
            blob_name=blob_name,
            user_delegation_key=user_delegation_key,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.now(timezone.utc) + timedelta(minutes=40)
        )

    async def upload_file(
                    self, container_name: str, local_file_path: str, semaphore = None,
                    blob_name: Optional[str] = None, enable_signature: Optional[bool] = True,
                    ) -> str:
        if semaphore:
            async with semaphore:
                return await self._upload_file(container_name, local_file_path, blob_name, enable_signature)
        return await self._upload_file(container_name, local_file_path, blob_name, enable_signature)
        
    async def _upload_file(
                        self, container_name: str, local_file_path: str, 
                        blob_name: Optional[str] = None, enable_signature: Optional[bool] = True) -> str:
        container_client = self.client.get_container_client(container_name)
        print("El blob", os.path.basename(local_file_path))
        blob_name = blob_name if blob_name else os.path.basename(local_file_path)
        
        async with container_client.get_blob_client(blob_name) as blob_client:
            with open(local_file_path, "rb") as data:
                await blob_client.upload_blob(data, overwrite=True)

        if not enable_signature:
            return blob_client.url

        sas_token = await self.generate_token(container_name, blob_name)
        return f"https://{self.storage_account}.blob.core.windows.net/{container_name}/{blob_name}?{sas_token}"

    async def upload_many_files(self, container_name: str, files_list: List[str],
                                max_concurrent: Optional[str] = 20 ) -> List[str]:
        
        semaphore = asyncio.Semaphore(max_concurrent)
        
        uplodad_tasks = [
            self.upload_file(
                container_name=container_name,
                local_file_path=current_file,
                semaphore=semaphore
            )
            for current_file in files_list
        ]

        process_results = await asyncio.gather(*uplodad_tasks, return_exceptions=True)

        successes = [result for result in process_results if not isinstance(result, Exception)]
        failures = [(files_list[i], result) for i, result in enumerate(process_results) 
                   if isinstance(result, Exception)]
        
        if failures:
            print(f"These files has been failure {len(failures)} -> {failures}")
        
        return successes
