import logging
from fastapi import APIRouter
from starlette.responses import JSONResponse
from app.config import get_settings

from app.presentation.api.dependencies import (
    get_handle_message_use_case,
    get_handle_message_stream_use_case,
    get_handle_threads_use_case
)

from app.presentation.streaming.sse import stream_response

logger = logging.getLogger(__name__)

BASE_PATH = "/api/v1/tools"

router = APIRouter(
    prefix=BASE_PATH
)


@router.get("users/{user_id}/")
async def get_agents_by_user_id(user_id: str):
    pass

@router.get("/{tool_id}/users/{user_id}/")
async def get_specific_agent_by_user_id(agent_id: str, user_id: str):
    pass