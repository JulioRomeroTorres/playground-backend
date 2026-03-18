import logging
from fastapi import APIRouter
from starlette.responses import JSONResponse
from fastapi.responses import StreamingResponse

from app.presentation.api.dependencies import (
    get_handle_message_use_case,
    get_handle_message_stream_use_case,
    get_handle_threads_use_case
)
from app.presentation.api.dto import (
    ConversationRequest, ConversationResponse
)
from app.presentation.streaming.sse import stream_response

logger = logging.getLogger(__name__)

BASE_PATH = "/api/v1/agents"

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

@router.get("users/{user_id}/")
async def get_agents_by_user_id(user_id: str):
    pass

@router.get("/{agent_id}/users/{user_id}/")
async def get_specific_agent_by_user_id(agent_id: str, user_id: str):
    pass

@router.post("/conversations/{conversation_id}/messages")
async def chat_agent(session_id: str, request: ConversationRequest):
    handle_message = get_handle_message_use_case()

    logger.info(f"Thread conversation {conversation_id}")

    response = await handle_message.execute(
        message=request.message,
        additional_files=request.additional_files,
        conversation_id=conversation_id
    )

    chat_response = ConversationResponse(
        content=response.message,
        metadata={**response.metadata, "model_name": response.model_name},
    )

    return JSONResponse(chat_response.model_dump(), headers={"status_code": "200"})
    pass

@router.post("/conversations/{session_id}/messages/stream")
async def chat_stream_agent(session_id: str, request: ConversationRequest):

    handle_message_stream = get_handle_message_stream_use_case()

    logger.info(f"Thread conversation {session_id}")

    async def generate():
        try:
            async for chunk in stream_response(
                handle_message_stream.execute(
                    message=request.message,
                    additional_files=request.additional_files,
                    conversation_id=session_id
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

@router.post("/question/")
async def question_agent(request: ConversationRequest):
    pass

@router.post("/conversations/")
async def generate_conversation_id():
    handle_threads = get_handle_threads_use_case()
    created_thread = await handle_threads.create()
    
    return JSONResponse(created_thread.model_dump(), headers={"status_code": "201"})
