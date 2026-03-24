from agent_framework import (
    Executor, ChatAgent, WorkflowContext,
    handler
) 

from app.domain.agent.agent import IntentClassification

class IntentClassifierExecutor(Executor):
    
    def __init__(self, 
                 classifier_agent: ChatAgent,
                 id: str = "intent_classifier"):
        super().__init__(id=id)
        self.classifier_agent = classifier_agent
        
    @handler
    async def handle(self, 
                     input_data: str,
                     ctx: WorkflowContext):

        classification_result = await self.classifier_agent.run(
            messages=input_data,
            response_format=IntentClassification
        )        
        await ctx.send_message(classification_result)
