import time
import logging
from typing import List, Any
from agent_framework import AgentRunResponse, ChatAgent
from app.domain.agent.telemetry import TelemetryProperties

class MonitoredChatAgent(ChatAgent):
    def __init__(self, *args, telemetry_properties: TelemetryProperties, log_level: int = logging.INFO,**kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(f"AgentFramework.{self.name or self.id}")
        self.log_level = log_level
        self.telemetry_properties = telemetry_properties

    def update_telemetry_properties(self, args: List[Any], agent_response: AgentRunResponse) -> AgentRunResponse:
        
        self.telemetry_properties.input_messages = self._normalize_messages(args[0])
        self.telemetry_properties.input_tokens = agent_response.usage_details.input_token_count
        self.telemetry_properties.output_messages = agent_response.messages
        self.telemetry_properties.output_tokens = agent_response.usage_details.output_token_count

        return agent_response

    async def run(self, *args, **kwargs) -> AgentRunResponse:
        start_time = time.time()

        #self._log_input(args, kwargs)
        agent_response = await super().run(*args, **kwargs)
        total_time = time.time() - start_time

        self.update_telemetry_properties(args, agent_response)
        agent_response.additional_properties = self.telemetry_properties.format_json()

        self._log_output(total_time, agent_response)

        return agent_response

    def _formatted_input(self, args, kwargs):
        if args and len(args) >= 1:
            messages = args[0]
            
        if 'messages' in kwargs:
            messages = kwargs['messages']

        return [msg if isinstance(messages, str) else msg.text for msg in  messages]
    
    def _log_input(self, args, kwargs) -> None:
        self.logger.log(self.log_level, f"📥 Input Agent: {self._formatted_input(args, kwargs)}")
    
    def _log_output(self, response_time, agent_response: AgentRunResponse) -> None:
        token_info = {
            "input_tokens": agent_response.usage_details.input_token_count,
            "output_tokens": agent_response.usage_details.output_token_count,
            "total_tokens": agent_response.usage_details.total_token_count
        }

        agent_response_metadata = {
            "tokens": token_info,
            "response": agent_response.to_dict()
        }

        self.logger.log(self.log_level, f"📥 Output Agent: {agent_response_metadata} in {response_time}")
        pass