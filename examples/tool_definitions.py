"""Reusable tool definitions for agentic workflows."""

TOOL_DEFINITIONS = [
    {
        "name": "search_documents",
        "description": "Search internal knowledge base for relevant documents",
        "parameters": {
            "query": {"type": "string", "description": "Search query"},
            "top_k": {"type": "integer", "default": 5},
        },
    },
    {
        "name": "execute_sql",
        "description": "Execute a read-only SQL query against the analytics database",
        "parameters": {
            "query": {"type": "string", "description": "SQL SELECT query"},
            "database": {"type": "string", "enum": ["analytics", "reporting"]},
        },
    },
    {
        "name": "send_notification",
        "description": "Send a notification to a Slack channel or email",
        "parameters": {
            "channel": {"type": "string"},
            "message": {"type": "string"},
            "priority": {"type": "string", "enum": ["low", "medium", "high"]},
        },
    },
]