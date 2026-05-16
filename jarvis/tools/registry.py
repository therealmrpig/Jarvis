import inspect
_T = {int: "integer", float: "number", bool: "boolean"}
class ToolRegistry:
    def __init__(self):
        self.tools = {}
    def register(self, name, description=""):
        def decorator(f):
            props, req = {}, []
            for n, p in inspect.signature(f).parameters.items():
                props[n] = {"type": _T.get(p.annotation, "string")}
                if p.default is inspect.Parameter.empty:
                    req.append(n)
            self.tools[name] = {"fn": f, "def": {"type": "function", "function": {"name": name, "description": description, "parameters": {"type": "object", "properties": props, "required": req}}}}
            return f
        return decorator
    def get_definitions(self):
        return [t["def"] for t in self.tools.values()]
    def execute(self, name, args):
        t = self.tools.get(name)
        if not t: return f"Tool '{name}' not found."
        try: return t["fn"](**args)
        except Exception as e: return f"Error executing tool '{name}': {str(e)}"
registry = ToolRegistry()