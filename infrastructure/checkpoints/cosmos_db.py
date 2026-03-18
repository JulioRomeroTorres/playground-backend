import asyncio
from dataclasses import asdict
from app.config import get_settings
from agent_framework import CheckpointStorage, WorkflowCheckpoint
from app.infrastructure.repository.cosmos_db import CosmosDbRepository
from app.domain.utils import filter_unnecesary_keys_from_dict

class CosmosDbCheckpointStorage(CheckpointStorage):
    def __init__(self, mode: str) -> None:
        settings = get_settings()
        self.mode = mode
        self.valid_keys = ['checkpoint_id', 'workflow_id', 'timestamp', 'messages', 'shared_state', 'pending_request_info_events', 'iteration_count', 'metadata', 'version']
        self.cosmos_db_client = CosmosDbRepository(settings.cosmos_db_chat_storage_url, settings.cosmos_db_chat_storage_db, 'WorkflowCheckpoint')
        pass
    
    async def save_checkpoint(self, checkpoint: WorkflowCheckpoint) -> str:
        checkpoint_dict = asdict(checkpoint)

        def _save_checkpoint():
            self.cosmos_db_client.insert_item(
                {
                    "id": checkpoint.checkpoint_id,
                    "mode": self.mode,
                    **checkpoint_dict
                    } 
                )
        await asyncio.to_thread(_save_checkpoint)
        print(f"Saved checkpoint {checkpoint.checkpoint_id} in cosmos")
        return checkpoint.checkpoint_id

    async def load_checkpoint(self, checkpoint_id: str) -> WorkflowCheckpoint | None:
        def _load_checkpoint():
            queryText = "SELECT * FROM workflowcheckpoint p WHERE p.id = @checkpoint_id"
            parameter = [
                dict(
                    name="@checkpoint_id",
                    value=checkpoint_id,
                )
            ]

            return self.cosmos_db_client.query_items(queryText, parameter)
        
        existing_item = await asyncio.to_thread(_load_checkpoint)
        existing_item = filter_unnecesary_keys_from_dict(existing_item, self.valid_keys)
        checkpoint = WorkflowCheckpoint(**existing_item)
        return checkpoint

    async def list_checkpoint_ids(self, workflow_id: str | None = None) -> list[str]:
        def _list_checkpoint_ids():
            queryText = "SELECT checkpoint_id FROM workflowcheckpoint p WHERE p.workflow_id = @workflow_id"
            parameter = [
                dict(
                    name="@workflow_id",
                    value=workflow_id,
                )
            ]

            return self.cosmos_db_client.query_items(queryText, parameter)
        
        workflow_data = await asyncio.to_thread(_list_checkpoint_ids)
        checkpoints: list[str] = [  item.get("checkpoint_id") for item in workflow_data ] 

        return checkpoints

    async def list_checkpoints(self, workflow_id: str | None = None) -> list[WorkflowCheckpoint]:
        def _list_checkpoints():
            queryText = "SELECT * FROM workflowcheckpoint wfc WHERE wfc.workflow_id = @workflow_id"
            parameter = [
                dict(
                    name="@workflow_id",
                    value=workflow_id,
                )
            ]

            return self.cosmos_db_client.query_items(queryText, parameter)
        
        workflow_data = await asyncio.to_thread(_list_checkpoints)
        checkpoints: list[WorkflowCheckpoint] = [ WorkflowCheckpoint.from_dict(filter_unnecesary_keys_from_dict(item, self.valid_keys)) for item in workflow_data ] 
        return checkpoints


    async def delete_checkpoint(self, checkpoint_id: str) -> bool:
        pass