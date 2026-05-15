import inspect
from typing import Callable, Any, Dict, List

class ToolRegistry:
    def __init__(self):
        self.tools = {}
    
    def register(self, name: str, description: str):
        # Decorator to register a function as a tool for Jarvis
        def decorator(func):
            self.tools[name] = {
                'function': func,
                'definition': {
                    "type": "function",
                    "function": {
                        "name": name,
                        "description": description,
                        "parameters": self._generate_schema(func)
                    }
                }
            }
            return func
        return decorator
    
    def _generate_schema(self, func: Callable) -> dict[str, Any]:
        # Automatically generate a JSON schema for the function's parameters
        sig = inspect.signature(func)
        parameters = {
            "type": "object",
            "properties": {},
            "required": []
        }

        for param_name, param in sig.parameters.items():
            # Map Python types to JSON schema types
            param_type = param.annotation
            json_type = "string"

            if param_type is int:
                json_type = "integer"
            elif param_type is float:
                json_type = "number"
            elif param_type is bool:
                json_type = "boolean"
            elif param_type is list:
                json_type = "array"
            elif param_type is dict:
                json_type = "object"

            parameters["properties"][param_name] = {
                "type": json_type,
                "description": f"The {param_name} parameter"
            }

            # If there's no default value, it's required
            if param.default == inspect.Parameter.empty:
                parameters["required"].append(param_name)

        return parameters
    
    def get_definitions(self) -> List[Dict[str, Any]]:
        # Return a list of tool definitions for Jarvis
        return [tool['definition'] for tool in self.tools.values()]
    
    def execute(self, name: str, arguments: Dict[str, Any]) -> Any:
        # Execute a registered tool by name with the provided arguments
        if name not in self.tools:
            return f"Tool '{name}' not found in registry."
        
        try:
            return self.tools[name]['function'](**arguments)
        except Exception as e:
            return f"Error executing tool '{name}': {str(e)}"

registry = ToolRegistry()