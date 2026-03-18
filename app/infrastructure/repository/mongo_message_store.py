from collections.abc import Sequence
from typing import Any, Optional
from uuid import uuid4
from agent_framework import ChatMessage
from app.domain.message_store.mongo_message_store import MongoMessageStore
from app.infrastructure.repository.mongo_db import MongoDbRepository
from app.domain.repository.chat_message_store import IChatMessageStore 
from app.domain.repository.history_converter import HistoryConverter
from app.domain.contants import LlmProviderEnum
from pymongo import DESCENDING as DSC
from datetime import datetime

class MongoChatMessageStore(IChatMessageStore):

    def __init__(
        self,
        db_repository: MongoDbRepository,
        thread_id: str, 
        max_messages: Optional[int] | None = None,
        key_prefix: Optional[str] = "thread",
        provider: Optional[LlmProviderEnum] = LlmProviderEnum.OPEN_AI
    ) -> None:

        self.db_repository = db_repository

        self.thread_id = thread_id or f"{uuid4()}"
        self.max_messages = max_messages
        self.key_prefix = key_prefix
        self.provider = provider
        self.history_converter = HistoryConverter(self.provider)

    @property
    def mongo_partition_key(self) -> str:
        return f"{self.key_prefix}:{self.thread_id}"

    async def add_messages(self, messages: Sequence[ChatMessage]) -> None:
        
        if not messages:
            return

        serialized_messages = [
            {
                "thread_id": self.thread_id, 
                "timestamp": datetime.now().timestamp(),
                **self._serialize_json_message(msg)
            } 
            for msg in messages]
        print(f"Serielized messages {serialized_messages}")
        await self.db_repository.batch_insert(serialized_messages)
        print("Messages saved")

        if self.max_messages is not None:
            
            filter = {"thread_id": self.thread_id}
            current_count = await self.db_repository.count_items(filter)

            if current_count > self.max_messages:
                
                pipeline = [
                {"$match": {"thread_id": self.thread_id}},
                {"$sort": {"timestamp": DSC}},
                {"$limit": self.max_messages},
                {"$group": {
                    "_id": None,
                    "min_timestamp": {"$min": "$timestamp"}
                }}
            ]

            result = await self.db_repository.aggregate(pipeline, max_length=1)
        
            if result:
                min_timestamp = result[0]["min_timestamp"]
                await self.db_repository.delete_many_items({
                    "thread_id": self.thread_id,
                    "timestamp": {"$lt": min_timestamp}
                })


    async def list_messages(self) -> list[ChatMessage]:

        pipeline = [
            {"$match": {"thread_id": self.thread_id}},
            {"$sort": {"timestamp": DSC}},
            {"$limit": 10}
        ]

        print("Getting Messages")
        last_messages = await self.db_repository.aggregate(pipeline)
        last_messages.reverse() 

        messages = []
        for serialized_message in last_messages:
            print("Seriataled Message", serialized_message, type(serialized_message))
            converted_serialized_message = self.history_converter.transform(serialized_message)
            message = self._deserialize_json_message(converted_serialized_message)
            messages.append(message)

        return messages

    async def serialize_state(self, **kwargs: Any) -> Any:
        
        state = MongoMessageStore(
            thread_id=self.thread_id,
            max_messages=self.max_messages,
        )
        return state.model_dump(**kwargs)
    
    #TODO
    async def serialize(self, **kwargs: Any) -> dict[str, Any]:
        return await self.serialize_state()
    
    #TODO
    async def deserialize(self, serialized_store_state: Any, **kwargs: Any) -> dict[str, Any]:
        return await self.deserialize_state(serialized_store_state)

    async def deserialize_state(self, serialized_store_state: Any, **kwargs: Any) -> None:
        if serialized_store_state:
            state = MongoMessageStore.model_validate(serialized_store_state, **kwargs)
            self.thread_id = state.thread_id
            self.max_messages = state.max_messages


    async def clear(self) -> None:
        await self.db_repository.delete_many_items({"thread_id": self.thread_id})