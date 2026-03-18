from typing import AsyncIterable, Any, List, Optional
from agent_framework import (
    ChatMessage, ChatResponse, ChatResponseUpdate,  
    ChatClientProtocol, ChatResponse, ChatMessage, 
    TextContent
) 
import asyncio
from app.infrastructure.repository.http import HttpRepository
from app.domain.agent.agent import ExternalAgentResponse
from app.domain.utils import replace_path_param
from app.config import get_settings

MessageAgentType = str | ChatMessage | list[str] | list[ChatMessage]

class ExternalClient(ChatClientProtocol):

    def __init__(self, 
                 base_url: str, 
                 conversation_id: Optional[str] = "",
                 chat_endpoint: Optional[str] = "",
                 stream_endpoint: Optional[str] = ""
                 ) -> None:
        self.conversation_id = conversation_id
        self.http_client = HttpRepository(replace_path_param(base_url, {"conversation_id": self.conversation_id}))

        self.chat_endpoint = replace_path_param(chat_endpoint, {"conversation_id": self.conversation_id})
        self.stream_endpoint = replace_path_param(stream_endpoint, {"conversation_id": self.conversation_id})
        pass

    @property
    def additional_properties(self) -> dict[str, Any]:
        return {}
    
    def format_string(self, value: str) -> dict[str, Any]:
        return {
            "message": value
        }

    def format_chat_message(self, value: ChatMessage) -> dict[str, Any]:
        return {
            "message": value.text
        }

    def mapper_list_value(self, value: List[Any]) -> list[dict[str, Any]]:
        if len(value) < 0:
            return {
                "message": "Sin mensajes"
            }
        last_message = value[-1]
        return self.mapper_instance_value(last_message)        

    def mapper_instance_value(self, value: MessageAgentType) -> dict[str, Any]:
        type_value = type(value)
        print(f"Message type {type_value} -> value: {value}")
        MAPPER_INSTANCE = {
            str: self.format_string,
            ChatMessage: self.format_chat_message,
            list: self.mapper_list_value,
        }
        return MAPPER_INSTANCE.get(type_value, lambda v: v)(value)

    def get_context_information(self) -> dict[str, Any]:
        settings = get_settings()
        return {
            "enduser_id": settings.app_end_user_id,
            "service_name": settings.app_service_name,
            "biz_unit": settings.app_biz_unit,
            "biz_domain": settings.app_biz_domain,
            "biz_subdomain": settings.app_biz_subdomain,
            "biz_process": settings.app_biz_process,
            "biz_subprocess": settings.app_biz_subprocess,
        }

    async def get_response(
        self,
        messages: MessageAgentType,
        **kwargs,
    ) -> ChatResponse:

        try:
            request_external_agent = self.mapper_instance_value(messages)
            print("RequestExternalAgent:", request_external_agent)
            context_information = self.get_context_information()

            agent_response = await self.http_client.post(self.chat_endpoint, { **request_external_agent, **context_information})
            external_agent_response = ExternalAgentResponse(**agent_response)

            return ChatResponse(
                messages=external_agent_response.get_messages(),
                response_id=external_agent_response.metadata.message_id,
                conversation_id=external_agent_response.metadata.conversation_id,
                model_id=external_agent_response.metadata.model_name,
                usage_details=external_agent_response.get_usage_details(),
                )
        except Exception as error:
            raise error

    def get_streaming_response(
        self,
        messages: MessageAgentType,
        **kwargs,
    ) -> AsyncIterable[ChatResponseUpdate]:
        async def _stream():
            try:
                yield ChatResponseUpdate(
                    contents=[TextContent(text="Method not implemented yet.")],
                    role="assistant",
                    message_id=""
                    ) 
            except Exception as error:
                raise error
        return _stream()

if __name__ == "__main__":
    async def main():
        client = ExternalClient("")
        assert isinstance(client, ChatClientProtocol)
    asyncio.run(main())