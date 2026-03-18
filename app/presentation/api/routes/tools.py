import logging
from fastapi import APIRouter
from starlette.responses import JSONResponse
from app.config import get_settings

from app.presentation.api.dependencies import (
    get_handle_tools_use_case
)

from app.presentation.streaming.sse import stream_response

from app.presentation.api.dto import (
    ToolInformationRequest
)

logger = logging.getLogger(__name__)

BASE_PATH = "/api/v1/tools"

router = APIRouter(
    prefix=BASE_PATH
)


@router.post("/users/{user_id}/")
async def create_tool(user_id: str, tool_information_request: ToolInformationRequest):
    handle_get_tools = get_handle_tools_use_case()
    tools_by_user = await handle_get_tools.create_tool(user_id, tool_information_request)

    return JSONResponse(tools_by_user.format_json(), headers={"status_code": "200"})

@router.get("/users/{user_id}/")
async def get_agents_by_user_id(user_id: str):
    handle_get_tools = get_handle_tools_use_case()
    tools_by_user = await handle_get_tools.get_tool_by_user(user_id)

    return JSONResponse(tools_by_user.model_dump(), headers={"status_code": "200"})

@router.get("/{tool_id}/users/{user_id}/")
async def get_specific_agent_by_user_id(tool_id: str, user_id: str):
    handle_get_tools = get_handle_tools_use_case()
    specific_tool = await handle_get_tools.get_tool_by_user(user_id, tool_id)

    return JSONResponse(specific_tool.model_dump(), headers={"status_code": "200"})