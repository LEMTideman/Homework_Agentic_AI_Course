from pydantic_ai import ToolCallPart

def collect_tools(messages) -> list[str]:
    """Return tool names in the order they were called."""
    tools = []

    for message in messages:
        for part in message.parts:
            if isinstance(part, ToolCallPart):
                tools.append(part.tool_name)

    return tools