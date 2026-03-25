from agent_framework.azure import AzureOpenAIChatClient
from agent_framework import (
    WorkflowBuilder,
    ChatAgent
) 

chat_client = AzureOpenAIChatClient(
    endpoint='',
    api_key='',
    deployment_name='gpt-4o-mini',
    api_version='2025-01-01-preview'
)

comida_agent = ChatAgent(
    chat_client=chat_client,
    name='comida-agent',
    instructions="Eres un agente especialista en comidas"
)

angela_agent = ChatAgent(
    chat_client=chat_client,
    name='angela-agent',
    instructions="Eres un agente especialista en comidas"
)

# Construir el workflow
workflow = (
    WorkflowBuilder()
    .register_agent(
        factory_func=lambda: comida_agent,
        name="comida-agent",
        output_response=True
    )
    .register_agent(
        factory_func=lambda: angela_agent,
        name="angela-agent",
        output_response=True
    )
    .add_edge("comida-agent", "angela-agent")  # comida -> angela
    .set_start_executor("comida-agent")  # El flujo empieza en comida
    .build()
)