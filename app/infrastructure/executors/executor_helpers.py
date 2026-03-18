import logging
from app.infrastructure.executors.executor_types import WorkflowOutput, WorkflowChunkOutput

logger = logging.getLogger(__name__)


class ExecutorHelpers:
    @staticmethod
    async def yield_error_output(
        ctx,
        error: Exception,
        agent_name: str,
        custom_message: str | None = None,
        metadata: dict | None = None
    ) -> None:
        logger.error(f"Error in {agent_name}: {error}", exc_info=True)

        error_message = custom_message or f"Error en {agent_name}: {str(error)}"
        error_metadata = metadata or {}
        error_metadata["error"] = str(error)

        output = WorkflowOutput(
            agent_name="error",
            message=error_message,
            confidence=0.0,
            metadata=error_metadata
        )
        await ctx.yield_output(output.model_dump_json())

    @staticmethod
    async def yield_success_output(
        ctx,
        agent_name: str,
        message: str,
        confidence: float,
        metadata: dict | None = None
    ) -> None:
        output = WorkflowOutput(
            agent_name=agent_name,
            message=message,
            confidence=confidence,
            metadata=metadata or {}
        )
        await ctx.yield_output(output.model_dump_json())

    @staticmethod
    async def yield_stream_chunk(
        ctx,
        agent_name: str,
        chunk: str,
        is_final: bool = False
    ) -> None:

        chunk_output = WorkflowChunkOutput(
            agent_name=agent_name,
            chunk=chunk,
            is_final=is_final   
        )

        await ctx.yield_output(chunk_output.model_dump_json())