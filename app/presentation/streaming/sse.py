import asyncio
import json
import logging
from datetime import datetime
from typing import Any, AsyncGenerator
from app.domain.exceptions import DomainException

logger = logging.getLogger(__name__)


async def format_sse(data: dict[str, Any]) -> str:
    json_data = json.dumps(data, ensure_ascii=False)
    return f"data: {json_data}\n\n"


async def stream_response(
    message_generator: AsyncGenerator[dict[str, Any], None]
) -> AsyncGenerator[str, None]:
    try:
        async for chunk in message_generator:
            yield await format_sse(chunk)
            await asyncio.sleep(0)
    
    except asyncio.CancelledError:
        logger.info("Stream cancelled by client")
        raise

    except Exception as e:
        logger.exception("Exception while generating response stream: %s", e)
        error_data = {
            "type": "error",
            "message": str(e),
            "error_type": type(e).__name__,
            "timestamp": datetime.now().isoformat(),
        }
        yield await format_sse(error_data)
