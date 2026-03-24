from typing import List
from app.domain.utils import (
    generate_uuid,
    get_datetime_now
)

from app.domain.agent.workflow import (
    SimplifyWorkflowInformation,
    CompletedWorkflowInformation
)

from app.application.services.agent_information_manager import AgentInformationManager

class HandleWorkflowsUseCase:
    def __init__(self, workflow_information_manager: AgentInformationManager):
        self.workflow_information_manager = workflow_information_manager
        pass

    async def create_workflow(self, user_id: str, workflow_information_request):
        completed_workflow_information = {
            "created_by": user_id, 
            "workflow_id": f"{generate_uuid()}", 
            "created_at": get_datetime_now(),
            **workflow_information_request.model_dump()
        }

        created_register = await self.workflow_information_manager.create_workflow(completed_workflow_information)
        return SimplifyWorkflowInformation(**created_register)

    async def update_workflow(self, workflow_id, workflow_information_request):
        current_workflow_information = await self.workflow_information_manager.get_specific_workflow_information(workflow_id)
        updated_information = {
            **current_workflow_information,
            **workflow_information_request.workflow_information_request,
            "updated_at": get_datetime_now()
        }

        await self.workflow_information_manager.update_workflow(workflow_id, updated_information)
        return updated_information

    async def get_workflows_by_user(self, user_id: str) -> List[SimplifyWorkflowInformation]:
        selected_workflows = await self.workflow_information_manager.get_workflows_by_user(user_id)
        return [ SimplifyWorkflowInformation(**workflow)  for workflow in selected_workflows ]
    
    async def get_specific_workflow_by_user(self, workflow_id: str) -> CompletedWorkflowInformation:
        selected_workflow = await self.workflow_information_manager.get_specific_workflow_information(workflow_id)
        return CompletedWorkflowInformation(**selected_workflow)