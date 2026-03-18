from pydantic import Field
from typing import Any, Dict, Annotated 
from app.domain.dispatcher.tool_settings import ToolSettings
from agent_framework import ai_function,  AIFunction
import json
from app.infrastructure.repository.http import HttpRepository

class DynamicToolFactory:
    
    @classmethod
    def create_tool(cls, tool_def: ToolSettings) -> Any:

        input_param_settings = (tool_def.input_parameters or {}).get("properties", {})
        valid_param_tool = input_param_settings.keys()
        
        async def dynamic_function(*args, **kwargs) -> str:
            seleted_args = {
                f"{param_name}": value
                for param_name, value in kwargs.items() if param_name in valid_param_tool
            }
            return await cls._execute_tool_logic(tool_def, seleted_args)
        
        final_tool = AIFunction(
            name=tool_def.name,
            description=tool_def.description,
            func=dynamic_function,
            input_model=tool_def.input_parameters,
        )
    
        return final_tool
    
    @staticmethod
    async def _execute_tool_logic(tool_def: ToolSettings, converted_args: Dict[str, Any]) -> str:
        print("tool_def.base_url", tool_def.base_url)
        http_client = HttpRepository(tool_def.base_url)
        response = await http_client.post(
            tool_def.endpoint,
            converted_args
        )

        return f"El resultado de la tool {tool_def.name} es {json.dumps(response)}"
    @staticmethod
    def _apply_annotations(func, fields: Dict):
        
        annotations = {}
        
        for param_name, (python_type, field) in fields.items():

            annotations[param_name] = Annotated[python_type, field]
        
        annotations['return'] = str
        func.__annotations__ = annotations
        return func