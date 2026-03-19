import logging
from fastapi import APIRouter
from starlette.responses import JSONResponse
from fastapi.responses import StreamingResponse

from app.presentation.api.dependencies import (
    get_handle_message_use_case,
    get_handle_message_stream_use_case,
    get_handle_threads_use_case,
    get_handle_agents_use_case
)
from app.presentation.api.dto import (
    ConversationRequest, ConversationResponse,
    AgentInformationRequest
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

@router.get("/")
async def get_agent_version(agent_name: str):
    handle_get_agents = get_handle_agents_use_case()
    agent_versions = await handle_get_agents.get_agent_version(agent_name)
    formatted_agents = [ agent_version.format_json() for agent_version in agent_versions ]
    return JSONResponse(formatted_agents, headers={"status_code": "200"})

@router.post("/users/{user_id}/")
async def create_agent(user_id: str, agent_information_request: AgentInformationRequest):
    handle_get_agents = get_handle_agents_use_case()
    created_agent = await handle_get_agents.create_agent(user_id, agent_information_request)

    return JSONResponse(created_agent.format_json(), headers={"status_code": "200"})

@router.get("/users/{user_id}/")
async def get_agents_by_user_id(user_id: str):
    handle_get_agents = get_handle_agents_use_case()
    agents_by_user = await handle_get_agents.get_agents_by_user(user_id)
    formatted_agents = [ agent.format_json() for agent in  agents_by_user ]
    return JSONResponse(formatted_agents, headers={"status_code": "200"})

@router.get("/{agent_id}/")
async def get_specific_agent_by_user_id(agent_id: str):
    handle_get_agents = get_handle_agents_use_case()
    specific_agent = await handle_get_agents.get_agent_by_user(agent_id)

    return JSONResponse(specific_agent.format_json(), headers={"status_code": "200"})

@router.post("/{agent_id}/conversations/{conversation_id}/messages")
async def chat_agent(agent_id: str, conversation_id: str, request: ConversationRequest):
    handle_message = get_handle_message_use_case()

    logger.info(f"Thread conversation {conversation_id}")

    response = await handle_message.execute(
        message=request.message,
        additional_files=request.additional_files,
        conversation_id=conversation_id,
        agent_id=agent_id
    )

    print("VAAAAAA", response)

    chat_response = ConversationResponse(
        content=response.message,
        metadata={**response.metadata, "model_name": response},
    )

    return JSONResponse(chat_response.model_dump(), headers={"status_code": "200"})

@router.post("/{agent_id}/conversations/{conversation_id}/messages/stream")
async def chat_stream_agent(agent_id: str, conversation_id: str, request: ConversationRequest):

    handle_message_stream = get_handle_message_stream_use_case()

    logger.info(f"Thread conversation {conversation_id}")

    async def generate():
        try:
            async for chunk in stream_response(
                handle_message_stream.execute(
                    message=request.message,
                    additional_files=request.additional_files,
                    conversation_id=conversation_id,
                    agent_id=agent_id
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

@router.post("/{agent_id}/question/")
async def question_agent(request: ConversationRequest):
    pass

@router.post("/conversations/")
async def generate_conversation_id():
    handle_threads = get_handle_threads_use_case()
    created_thread = await handle_threads.create()
    
    return JSONResponse(created_thread.model_dump(), headers={"status_code": "201"})
