import json
from typing import Annotated, Sequence, TypedDict

from langchain_core.messages import BaseMessage, SystemMessage, ToolMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]


def create_react_agent(model, tools, prompt: str, stop_tools: list[str] | None = None):

    if stop_tools is None:
        stop_tools = []

    model = model.bind_tools(tools)
    tools_by_name = {tool.name: tool for tool in tools}

    def tool_node(state: AgentState):
        outputs = []
        for tool_call in state["messages"][-1].tool_calls:
            tool_result = tools_by_name[tool_call["name"]].invoke(tool_call["args"])
            outputs.append(
                ToolMessage(
                    content=json.dumps(tool_result),
                    name=tool_call["name"],
                    tool_call_id=tool_call["id"],
                )
            )
        return {"messages": outputs}

    def call_model(
        state: AgentState,
        config: RunnableConfig,
    ):
        system_prompt = SystemMessage(
            f"Use the tools to answer as best as you can!\nPAY ATTENTION to the following instructions:\n{prompt}"
        )
        response = model.invoke([system_prompt] + state["messages"], config)
        return {"messages": [response]}

    def should_continue(state: AgentState):
        messages = state["messages"]
        last_message = messages[-1]
        if isinstance(last_message, ToolMessage):
            if last_message.name in stop_tools:
                return "end"
            return "continue"
        if not last_message.tool_calls:
            return "end"
        else:
            return "continue"

    workflow = StateGraph(AgentState)

    workflow.add_node("agent", call_model)
    workflow.add_node("tools", tool_node)

    workflow.set_entry_point("agent")

    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "continue": "tools",
            "end": END,
        },
    )

    workflow.add_conditional_edges(
        "tools", should_continue, {"continue": "agent", "end": END}
    )

    graph = workflow.compile()
    return graph
