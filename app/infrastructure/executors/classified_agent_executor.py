from agent_framework import (
    handler, AgentExecutor, WorkflowContext
)

import asyncio

from app.domain.agent.agent import IntentClassification

class ClassifiedAgentExecutor(AgentExecutor):
    def __init__(self, agent, *, agent_thread = None, output_response = False, id = None):
        super().__init__(agent, agent_thread=agent_thread, output_response=output_response, id=id)
        self.classified_agent = agent
    
    @handler
    async def handle_classification(self, input_data: IntentClassification, ctx: WorkflowContext):
        classification_result = await self.classified_agent.run(
            messages=input_data.original_message
        )        
        print("Vasss  a caer cpp", classification_result, "pregunta", input_data)

        await asyncio.gather(
            ctx.send_message(classification_result),
            ctx.yield_output(classification_result.to_dict()) 
            )           