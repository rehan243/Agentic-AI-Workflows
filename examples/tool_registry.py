"""Production Tool Registry for Agentic AI Systems - Rehan Malik"""

import json
from typing import Callable, Any
from functools import wraps


class ToolRegistry:
    def __init__(self):
        self._tools = {}

    def register(self, name: str, description: str, params: dict):
        def decorator(fn: Callable):
            self._tools[name] = {
                "name": name, "description": description,
                "parameters": {"type": "object", "properties": params},
                "handler": fn
            }
            @wraps(fn)
            def wrapper(*args, **kwargs):
                return fn(*args, **kwargs)
            return wrapper
        return decorator

    def get_schemas(self) -> list[dict]:
        return [{"type": "function", "function": {
            "name": t["name"], "description": t["description"],
            "parameters": t["parameters"]}} for t in self._tools.values()]

    def execute(self, name: str, args: dict) -> dict:
        if name not in self._tools:
            return {"error": f"Tool '{name}' not found"}
        try:
            return {"result": self._tools[name]["handler"](**args)}
        except Exception as e:
            return {"error": str(e)}


registry = ToolRegistry()

@registry.register("search", "Search knowledge base", {"query": {"type": "string"}})
def search(query: str):
    return {"results": [f"Result for: {query}"], "count": 1}

@registry.register("calculate", "Math calculations", {"expr": {"type": "string"}})
def calculate(expr: str):
    safe = set("0123456789+-*/.() ")
    if all(c in safe for c in expr):
        return {"result": eval(expr, {"__builtins__": {}}, {})}
    return {"error": "Invalid expression"}

if __name__ == "__main__":
    print("Tools:", [s["function"]["name"] for s in registry.get_schemas()])
    print(registry.execute("search", {"query": "RAG patterns"}))
    print(registry.execute("calculate", {"expr": "2**10 + 42"}))
