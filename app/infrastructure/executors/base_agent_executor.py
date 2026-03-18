import logging
from typing import Never, cast
from abc import ABC
import time

from agent_framework import AgentRunResponse, ChatAgent, AgentExecutor, WorkflowContext

from app.application.services.conversation_manager import ConversationManager
from app.domain.agent import MailboxAgentOutput
from app.infrastructure.executors.executor_types import IntentClassification
from app.infrastructure.executors.executor_helpers import ExecutorHelpers

logger = logging.getLogger(__name__)


class BaseAgentExecutor(AgentExecutor, ABC):
    def __init__(
        self,
        executor_id: str,
        agent: ChatAgent,
        conversation_manager: ConversationManager,
        workflow
    ):
        self.conversation_manager = conversation_manager
        self.agent = agent
        self.workflow = workflow

        super().__init__(agent=agent)
        self.executor_id = executor_id
        
        self.helpers = ExecutorHelpers()
    
    

    def _get_thread(self, agent_name: str = None):
        if agent_name is None:
            agent_name = self.id
        session_id = self.workflow.current_session_id
        print("SESSION ID", session_id)
        return self.conversation_manager.get_or_create_thread(
            session_id=session_id,
            agent_name=agent_name,
            agent=self.agent
        )

class BaseAgentExecutorWithFallback(BaseAgentExecutor):
    async def _fallback_to_mailbox(
        self,
        classification: IntentClassification,
        ctx: WorkflowContext[Never, str],
        source_agent: str
    ) -> None:
        session_id = self.workflow.current_session_id

        mailbox_thread = self.conversation_manager.get_or_create_thread(
            session_id=session_id,
            agent_name="mailbox_agent",
            agent=self.workflow.mailbox_executor.agent
        )

        try:
            response = await self.workflow.mailbox_executor.agent.run(
                classification.original_message,
                thread=mailbox_thread,
                response_format=MailboxAgentOutput
            )
            mailbox_output = cast(MailboxAgentOutput, response.value)
            response_text = mailbox_output.result

            logger.info(f"✅ Mailbox response (fallback from {source_agent}): {response_text[:100]}...")

            await self.helpers.yield_success_output(
                ctx=ctx,
                agent_name="mailbox_agent",
                message=response_text,
                confidence=0.8,  # Moderate confidence for fallback
                metadata={
                    "reasoning": f"Fallback from {source_agent}",
                    "original_intent": classification.intent,
                    "action": mailbox_output.action,
                    "summary": mailbox_output.summary
                }
            )

        except Exception as e:
            await self.helpers.yield_error_output(
                ctx=ctx,
                error=e,
                agent_name=source_agent,
                custom_message=f"Error en fallback a Mailbox: {str(e)}"
            )
