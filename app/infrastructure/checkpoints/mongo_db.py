from dataclasses import asdict
from typing import Any
from app.config import get_settings
from agent_framework import CheckpointStorage, WorkflowCheckpoint
from app.infrastructure.repository.mongo_db import MongoDbRepository
from app.domain.utils import filter_unnecesary_keys_from_dict

class MongoDbCheckpointStorage(CheckpointStorage):
    def __init__(self, mode: str, mongo_client: Any) -> None:
        settings = get_settings()
        self.mode = mode
        self.valid_keys = ['checkpoint_id', 'workflow_id', 'timestamp', 'messages', 'shared_state', 'pending_request_info_events', 'iteration_count', 'metadata', 'version']
        self.db_repository = MongoDbRepository(mongo_client, settings.mongo_db_name, 'workflow_checkpoint')
        pass
    
    async def save_checkpoint(self, checkpoint: WorkflowCheckpoint) -> str:
        checkpoint_dict = asdict(checkpoint)
        await self.db_repository.insert_item({
            "checkpoint_id": checkpoint.checkpoint_id,
            "mode": self.mode,
            **checkpoint_dict
        })
        print(f"Saved checkpoint {checkpoint.checkpoint_id} in cosmos")
        return checkpoint.checkpoint_id

    async def load_checkpoint(self, checkpoint_id: str) -> WorkflowCheckpoint | None:
        existing_item = await self.db_repository.get_items_by_filter({"checkpoint_id": checkpoint_id})
        
        if len(existing_item) < 0:
            raise ValueError("")
        
        existing_item = existing_item[0]
        existing_item = filter_unnecesary_keys_from_dict(existing_item, self.valid_keys)
        checkpoint = WorkflowCheckpoint(**existing_item)
        return checkpoint

    async def list_checkpoint_ids(self, workflow_id: str | None = None) -> list[str]:
                
        workflow_data = await self.db_repository.get_items_by_filter({"workflow_id": workflow_id}, {"checkpoint_id": 1, "_id": 0})
        checkpoints: list[str] = [  item.get("checkpoint_id") for item in workflow_data ] 

        return checkpoints

    async def list_checkpoints(self, workflow_id: str | None = None) -> list[WorkflowCheckpoint]:
        workflow_data = await self.db_repository.get_items_by_filter({"workflow_id": workflow_id})
        checkpoints: list[WorkflowCheckpoint] = [ WorkflowCheckpoint.from_dict(filter_unnecesary_keys_from_dict(item, self.valid_keys)) for item in workflow_data ] 
        return checkpoints


    async def delete_checkpoint(self, checkpoint_id: str) -> bool:
        await self.db_repository.collection.find_one_and_delete({"checkpoint_id": checkpoint_id})
        print(f"Deleted checkpoint {checkpoint_id} from cosmos")
        return True