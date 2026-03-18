from typing import Dict, Any
from app.domain.contants import LlmProviderEnum

JsonType = Dict[str, Any]

class HistoryConverter:
    def __init__(self, llm_provider: LlmProviderEnum):
        self.llm_provider = llm_provider
    

    def open_ai_transform_message(self, message: JsonType) -> JsonType:
        
        current_message = message.copy()
    
        role = message.get("role", {}).get("value")
        contents = message.get("contents", [])
        
        if role == "assistant":
            new_contents = []
            for content in contents:
                if content.get("type") == "function_call":
                    new_contents.append({
                        "type": "tool_call",
                        "call_id": content.get("call_id"),
                        "name": content.get("name"),
                        "arguments": content.get("arguments")
                    })
                else:
                    new_contents.append(content)
            
            current_message["contents"] = new_contents
        
        if role == "tool":
            new_contents = []
            for content in contents:
                if content.get("type") == "function_result":
                    result = content.get("result")
                    new_contents.append({
                        "type": "tool_result",
                        "call_id": content.get("call_id"),
                        "result": result
                    })
                else:
                    new_contents.append(content)
            
            current_message["contents"] = new_contents
        
        return current_message

    def anthopic_transform_message(self, message: JsonType) -> JsonType:
        pass
    
    def deep_seek_transform_message(self, message: JsonType) -> JsonType:
        pass

    def transform(self, message: str) -> str:

        MAPPER_HISTORY_MESSAGE = {
            LlmProviderEnum.OPEN_AI: self.open_ai_transform_message,
            LlmProviderEnum.ANTHROPIC: self.anthopic_transform_message,
            LlmProviderEnum.DEEP_SEEK: self.deep_seek_transform_message,
        }

        return MAPPER_HISTORY_MESSAGE[self.llm_provider](message)