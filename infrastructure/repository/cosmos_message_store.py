from collections.abc import Sequence
from typing import Any, Optional
from uuid import uuid4
import redis.asyncio as redis
from agent_framework import ChatMessage
from app.infrastructure.repository.cosmos_db import CosmosDbRepository
from app.domain.repository.chat_message_store import ChatMessageStore 
from app.domain.message_store.cosmos_message_store import CosmosMessageStore

class CosmosChatMessageStore(ChatMessageStore):

    def __init__(
        self,
        url: str,
        database_name: str,
        container_name: str,
        thread_id: str, 
        max_messages: Optional[int] | None = None,
        key_prefix: Optional[str] = "thread" 
    ) -> None:

        self.url = url
        self.database_name = database_name
        self.container_name = container_name

        self.cosmos_db_client = CosmosDbRepository(url, database_name, container_name)

        self.thread_id = thread_id or f"{uuid4()}"
        self.max_messages = max_messages
        self.key_prefix = key_prefix

    @property
    def cosmos_partition_key(self) -> str:
        return f"{self.key_prefix}:{self.thread_id}"

    async def add_messages(self, messages: Sequence[ChatMessage]) -> None:
        
        if not messages:
            return

        serialized_messages = [
            {
                "id": f"{uuid4()}",
                "thread_id": self.thread_id, 
                **self._serialize_json_message(msg)
            } 
            for msg in messages]
        print(f"Serielized messages {serialized_messages}")
        self.cosmos_db_client.batch_insert(serialized_messages, self.thread_id)
        print("Messages saved")

        if self.max_messages is not None:
            
            sql_query = """
                COUNT(*) 
                FROM historical 
                WHERE historical.thread_id = @tid
            """

            parameters = [
                {"name": "@tid", "value": self.thread_id}
            ]

            current_count = len(self.cosmos_db_client.query_items(
                query=sql_query,
                parameters=parameters
            ))

            if current_count > self.max_messages:
                await self.cosmos_db_client.delete_item()

    async def list_messages(self) -> list[ChatMessage]:

        sql_query = """
            SELECT TOP 10 * 
            FROM historical hist 
            WHERE hist.thread_id = @tid 
            ORDER BY hist.timestamp DESC
        """

        parameters = [
            {"name": "@tid", "value": self.thread_id}
        ]

        print("Getting Messages")
        items_iterator = self.cosmos_db_client.query_items(
            query=sql_query,
            parameters=parameters 
        )

        last_messages = list(items_iterator)
        last_messages.reverse() 

        messages = []
        for serialized_message in last_messages:
            print("Seriataled Message", serialized_message, type(serialized_message))
            message = self._deserialize_json_message(serialized_message)
            messages.append(message)

        return messages

    async def serialize_state(self, **kwargs: Any) -> Any:
        
        state = CosmosMessageStore(
            thread_id=self.thread_id,
            max_messages=self.max_messages,
            url=self.url,
            database=self.database_name,
            container=self.container_name
        )
        return state.model_dump(**kwargs)

    async def deserialize_state(self, serialized_store_state: Any, **kwargs: Any) -> None:
        
        if serialized_store_state:
            state = CosmosMessageStore.model_validate(serialized_store_state, **kwargs)
            self.thread_id = state.thread_id
            self.max_messages = state.max_messages

            if state.url and state.url != self.url:
                self.url = state.url
                self.database_name = state.database
                self.container_name = state.container

                self.cosmos_db_client = CosmosDbRepository(self.url, self.database_name, self.container_name)

    async def clear(self) -> None:
        await self.cosmos_db_client.delete_item()

    async def aclose(self) -> None:
        pass