import json
from typing import Dict, Any
from agent_framework import ChatMessage
from collections.abc import Sequence

class IChatMessageStore:
    async def add_messages(self, messages: Sequence[ChatMessage]) -> None:
        pass

    async def list_messages(self) -> list[ChatMessage]:
        pass 

    async def serialize_state(self, **kwargs: Any) -> Any:
        pass

    async def deserialize_state(self, serialized_store_state: Any, **kwargs: Any) -> None:
        pass

    def _serialize_message(self, message: ChatMessage) -> str:
        message_dict = message.to_dict()
        return json.dumps(message_dict, separators=(",", ":"))

    def _serialize_json_message(self, message: ChatMessage) -> str:
        return message.to_dict()
        
    def _deserialize_message(self, serialized_message: str) -> ChatMessage:
        message_dict = json.loads(serialized_message)
        return ChatMessage.from_json(message_dict)

    def _deserialize_json_message(self, serialized_message: Dict[str, Any]) -> ChatMessage:
        return ChatMessage.from_dict(serialized_message)

    async def clear(self) -> None:
        pass

    async def aclose(self) -> None:
        pass