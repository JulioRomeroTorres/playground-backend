import logging
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from starlette.responses import JSONResponse
from app.config import get_settings

from app.presentation.api.dependencies import (
    get_handle_message_use_case,
    get_handle_message_stream_use_case,
    get_handle_threads_use_case
)
from app.presentation.api.dto import (
    ConversationFilters,
    ConversationRequest, ConversationResponse
)
from app.presentation.streaming.sse import stream_response

logger = logging.getLogger(__name__)

BASE_PATH = "/api/v1"

router = APIRouter(
    prefix=BASE_PATH
)

STREAMING_HEADERS = {
    "Content-Type": "text/event-stream",
    "Cache-Control": "no-cache, no-transform",
    "Connection": "keep-alive",
    "X-Accel-Buffering": "no",
    "Transfer-Encoding": "chunked"
}

@router.post("/conversations/{conversation_id}/")
async def chat(conversation_id: str, conversation_request: ConversationRequest):
    handle_message = get_handle_message_use_case()

    logger.info(f"Thread conversation {conversation_id}")

    response = await handle_message.execute(
        message=conversation_request.message,
        additional_files=conversation_request.additional_files,
        conversation_id=conversation_id,
        additional_information=conversation_request.additional_information,
        trace=conversation_request.trace.to_json()
    )

    chat_response = ConversationResponse(
        content=response.message,
        metadata={**response.metadata, "model_name": get_settings().azure_openai_deployment},
    )

    return JSONResponse(chat_response.model_dump(), headers={"status_code": "200"})


@router.post("/conversations/{conversation_id}/stream/")
async def chat_stream(conversation_id: str, conversation_request: ConversationRequest):
    handle_message_stream = get_handle_message_stream_use_case()

    logger.info(f"Thread conversation {conversation_id}")

    async def generate():
        try:
            async for chunk in stream_response(
                handle_message_stream.execute(
                    message=conversation_request.message,
                    additional_files=conversation_request.additional_files,
                    conversation_id=conversation_id,
                    additional_information=conversation_request.additional_information,
                    trace=conversation_request.trace.to_json()
                )
            ):
                yield chunk
        except Exception as e:
            raise e


    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers=STREAMING_HEADERS
    )

@router.post("/conversations/")
async def generate_thread_conversation():
    handle_threads = get_handle_threads_use_case()
    created_thread = await handle_threads.create()
    
    return JSONResponse(created_thread.model_dump(), headers={"status_code": "201"})

@router.get("/conversations/")
async def get_conversations():
    handle_threads = get_handle_threads_use_case()
    selected_conversations = await handle_threads.get(ConversationFilters)
    return JSONResponse(selected_conversations.model_dump(), headers={"status_code": "200"})