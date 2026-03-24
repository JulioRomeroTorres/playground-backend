import logging
from fastapi import APIRouter
from starlette.responses import JSONResponse
from fastapi.responses import StreamingResponse

from app.presentation.api.dependencies import (
    get_handle_workflows_use_case,
    get_handle_workflows_message_use_case
)
from app.presentation.api.dto import (
    ConversationRequest, ConversationResponse,
    WorkflowInformationRequest
)

logger = logging.getLogger(__name__)

BASE_PATH = "/api/v1/workflows"

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

@router.post("/users/{user_id}/")
async def create_workflow(user_id: str, workflow_information_request: WorkflowInformationRequest):
    handle_create_workflow = get_handle_workflows_use_case()
    created_agent = await handle_create_workflow.create_workflow(user_id, workflow_information_request)

    return JSONResponse(created_agent.format_json(), headers={"status_code": "200"})

@router.put("/{workflow_id}/")
async def create_workflow(workflow_id: str, workflow_information_request: WorkflowInformationRequest):
    handle_get_agents = get_handle_workflows_use_case()
    created_agent = await handle_get_agents.update_workflow(workflow_id, workflow_information_request)

    return JSONResponse({}, headers={"status_code": "200"})

@router.get("/users/{user_id}/")
async def get_workflows_by_user_id(user_id: str):
    handle_workflows = get_handle_workflows_use_case()
    workflows_by_user = await handle_workflows.get_workflows_by_user(user_id)
    formatted_workflows = [ workflow_by_user.format_json() for workflow_by_user in workflows_by_user ]
    return JSONResponse(formatted_workflows, headers={"status_code": "200"})

@router.get("/{workflow_id}/")
async def get_specific_workflow_by_user_id(workflow_id: str):
    handle_get_agents = get_handle_workflows_use_case()
    specific_agent = await handle_get_agents.get_specific_workflow_by_user(workflow_id)

    return JSONResponse(specific_agent.format_json(), headers={"status_code": "200"})

@router.post("/{agent_id}/conversations/{conversation_id}/messages")
async def chat_workflow(agent_id: str, conversation_id: str, request: ConversationRequest):
    handle_message = get_handle_workflows_message_use_case()

    logger.info(f"Thread conversation {conversation_id}")

    response = await handle_message.execute(
        message=request.message,
        additional_files=request.additional_files,
        conversation_id=conversation_id,
        agent_id=agent_id
    )

    chat_response = ConversationResponse(
        content=response.message,
        metadata={**response.metadata, "model_name": response},
    )

    return JSONResponse(chat_response.model_dump(), headers={"status_code": "200"})