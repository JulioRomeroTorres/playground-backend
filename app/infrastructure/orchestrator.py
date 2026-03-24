import logging
from typing import (
    Union, List, Any, 
    Dict, Optional, AsyncIterable
) 

from app.domain.utils import get_metadata_from_uri
from app.domain.agent.agent import (
    AgentSettings, WorkflowSettings, 
    IntentClassification
)

from agent_framework import (
    UriContent, 
    TextContent, ChatMessage
    )

from app.infrastructure.agents.agnostic_agent import AgnosticAgent
from agent_framework import (
    WorkflowBuilder, 
    Case, Default, WorkflowExecutor, AgentExecutor,
    ConcurrentBuilder,
    Workflow, WorkflowRunResult, WorkflowEvent
)

from app.infrastructure.executors.intent_classifier_executor import IntentClassifierExecutor
from app.domain.orchestrator.service import IWorkflowOrchestrator

logger = logging.getLogger(__name__)

class WorkflowOrchestrator(IWorkflowOrchestrator):
    def __init__(
        self,
        db_client: Any
    ) -> None:
        
        self.agent_garden: Dict[str, Any] = {}
        self.workflow:Workflow = None
        self.db_client = db_client

    def create_agent(self, agent_settings: AgentSettings, conversation_id: Optional[str] = None) -> None:
        agent = AgnosticAgent(conversation_id, agent_settings, self.db_client)

        self.agent_garden[agent_settings.id] = {
            "type": "agent",
            "name": agent_settings.name,
            "description": agent_settings.description,
            "content": agent
        }

    def generate_switch_case_edge_group(self, agents_ids: List[str], default_agent_id: str) -> List[Any]:
        
        switch_conditions = []
        default_target_executor = AgentExecutor(
            agent=self.agent_garden[default_agent_id].get("content").agent,
            id=self.agent_garden[default_agent_id].get("name")
        )

        for index, agent_id in enumerate(agents_ids):
            current_agent = self.agent_garden[agent_id].get("content").agent
            name = self.agent_garden[agent_id].get("name")

            agent_executor = AgentExecutor(
                agent=current_agent,
                id=name
            )

            switch_conditions.append(
                Case(
                    condition=lambda msg, idx=index: isinstance(msg, IntentClassification) and msg.intent == name,
                    target=agent_executor
                )
            )

        return [*switch_conditions, Default(target=default_target_executor)]

    def generate_classifier_agent(self, workflow_id: str, agent_ids: List[str]):

        rules = [
            f"""
            -{self.agent_garden[agent_id]["name"]}: Si se trata de temas relacionados con {self.agent_garden[agent_id]["description"]}
            """
            for agent_id in agent_ids
        ]

        agent_settings = AgentSettings(
            name=f"classifier-agent-{workflow_id}",
            system_instruction=f"""
                Eres un agente especialista en clasificar la intencion del usuario
                en base a las siguientes categorias:
                {
                    '\n'.join(rules)
                }
                Como respuesta indicaras la etiqueta asi como también el porqué elegiste ello
            """,
            tools=[],            
            model='gpt-4o-mini',
            id=f"classifier-agent-{workflow_id}"
        )
        agent_wrapper = AgnosticAgent(None, agent_settings, self.db_client)
        return agent_wrapper.agent

    def create_sub_workflow(self, sub_workflow_settings: WorkflowSettings): 
        workflow_builder = WorkflowBuilder()
        agent_garden_type = "workflow"

        if sub_workflow_settings.sub_type == 'sequential':
            for agent_id in sub_workflow_settings.sub_agents:
                current_agent = self.agent_garden[agent_id].get("content")
                workflow_builder.register_agent(
                    factory_func=current_agent.agent,
                    name=current_agent.get_agent_name()
                )

            initial_agent = self.agent_garden[sub_workflow_settings.sub_agents[0]].get("content")
            workflow_builder.set_start_executor(initial_agent.get_agent_name())
            
            self.agent_garden[sub_workflow_settings.id] = {
                "type": agent_garden_type,
                "name": sub_workflow_settings.id,
                "content": workflow_builder.build()
            } 
        
        if sub_workflow_settings.sub_type == 'parallel':
            participants = [ self.agent_garden[agent_id].get("content").agent for agent_id in sub_workflow_settings.sub_agents ]
            self.agent_garden[sub_workflow_settings.id] = {
                "type": agent_garden_type,
                "name": sub_workflow_settings.id,
                "content": ConcurrentBuilder().participants(participants).build()
            } 

        if sub_workflow_settings.sub_type == 'switch':
            classifier_executor = IntentClassifierExecutor(
                
                sub_workflow_settings.id
            )
            builder = (
                WorkflowBuilder()
                .set_start_executor(classifier_executor)
                .add_switch_case_edge_group(
                    classifier_executor,
                    self.generate_switch_case_edge_group(sub_workflow_settings.sub_agents[0:-1], sub_workflow_settings.sub_agents[-1])
                )
                .build()
            )

            self.agent_garden[sub_workflow_settings.id] = {
                "type": agent_garden_type,
                "name": sub_workflow_settings.id,
                "content": builder
            } 


    def build_workflow(self, workflow_structure: Any) -> None:
        workflow_builder = WorkflowBuilder()

        for node in workflow_structure.nodes:
            if node.type == "agent":
                workflow_builder.register_agent(
                    factory_func=self.agent_garden[node.id].get("content").agent,
                    name=self.agent_garden[node.id].get("name")
                )
            else:
                workflow_builder.register_executor(
                    factory_func=WorkflowExecutor(
                        workflow=self.agent_garden[node.id].get("content"),
                        id=self.agent_garden[node.id].get("name"),
                        allow_direct_output=False,
                        propagate_request=True
                    ),
                    name=self.agent_garden[node.id].get("name")
                )
        
        for edge in workflow_structure.edges:
            workflow_builder.add_edge(
                self.agent_garden[edge.source].get("name"),
                self.agent_garden[edge.target].get("name")
            )

        self.workflow = (
            workflow_builder.set_start_executor(
                AgentExecutor(
                    self.agent_garden[workflow_structure.start_node]["content"]
                )
            )
            .build()
        )
    
    def create_uri_content(self, metadata: Dict[str, str]):
        return UriContent(uri=metadata.get('uri'), media_type=metadata.get('media_type'))
    
    def prepare_content(
                    self, message: str, additional_files: Optional[List[str]] = []
                    ) -> ChatMessage:
        
        additional_content_files = [
            self.create_uri_content(get_metadata_from_uri(additional_file))
            for additional_file in additional_files
        ]

        return ChatMessage(
            role="user",
            contents=[ TextContent(text=message) ,*additional_content_files]
        ) 

    async def generate_stream_content(self, message: str, additional_files: Optional[List[str]] = []) -> AsyncIterable[WorkflowEvent]:
        content = self.prepare_content(message, additional_files)
        async for event in self.workflow.run_stream(content):
            yield event
    
    async def generate_content(self, message: str, additional_files: Optional[List[str]] = []) -> WorkflowRunResult:
        content = self.prepare_content(message, additional_files)
        workflow_response = await self.workflow.run(content)
        return workflow_response