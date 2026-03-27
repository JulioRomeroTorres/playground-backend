from agent_framework import (
    Executor, ChatAgent, WorkflowContext,
    ChatMessage, AgentExecutorResponse, SubWorkflowRequestMessage, AgentRunResponse,
    handler
) 
from typing import List
from app.domain.agent.agent import IntentClassification

class IntentClassifierExecutor(Executor):
    
    def __init__(self, 
                 classifier_agent: ChatAgent,
                 id: str = "intent_classifier"):
        super().__init__(id=id)
        self.classifier_agent = classifier_agent
    
    async def _classify_text(self, input_data: str, ctx: WorkflowContext):
        classification_result = await self.classifier_agent.run(
            messages=input_data,
            response_format=IntentClassification
        )
        await ctx.send_message(classification_result.value)        

    @handler
    async def handle(self, 
                     input_data: str,
                     ctx: WorkflowContext):
        await self._classify_text(input_data, ctx)

    @handler
    async def handle_agent_response(self, input_data: AgentExecutorResponse, ctx: WorkflowContext):
        await self._classify_text(input_data.agent_run_response.text, ctx)

    @handler
    async def handle_chat_message(self, input_data: ChatMessage, ctx: WorkflowContext):
        await self._classify_text(input_data, ctx)
    
    @handler
    async def handle_workflow_as_agent_message(self, input_data: List[ChatMessage], ctx: WorkflowContext):
        await self._classify_text(input_data, ctx)
    
    @handler
    async def handle_workflow_message(self, input_data: SubWorkflowRequestMessage, ctx: WorkflowContext):
        await self._classify_text(input_data, ctx)
