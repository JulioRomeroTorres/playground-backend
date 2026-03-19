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
async def get_tools_by_user_id(user_id: str):
    handle_get_tools = get_handle_tools_use_case()
    tools_by_user = await handle_get_tools.get_tools_by_user(user_id)
    formatted_information = [ tool.format_json() for tool in tools_by_user ]
    return JSONResponse(formatted_information, headers={"status_code": "200"})

@router.get("/{tool_id}/")
async def get_tool_agent_by_user_id(tool_id: str):
    handle_get_tools = get_handle_tools_use_case()
    specific_tool = await handle_get_tools.get_tool_by_user(tool_id)

    return JSONResponse(specific_tool.format_json(), headers={"status_code": "200"})