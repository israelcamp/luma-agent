import json
from typing import Annotated

from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict

from llms.auth import AuthLLM
from llms.react import ReactAgent


class State(TypedDict):
    authenticated: bool
    name: str
    phone: str
    date_of_birth: str
    messages: Annotated[list, add_messages]
    stop: bool
    input: str
    answer: str

def check_auth(state: State) -> State:
    if state.get("authenticated", False):
        return state

    infos = AuthLLM.run(
        input=state["input"]
    )
    state.update(infos)

    if all(state.get(key, None) is not None for key in (
        "name", "phone", "date_of_birth"
    )):
        state["authenticated"] = True
        state["answer"] = "You are authenticated"
        return state

    msg = "To continue I need some information:\n"
    if state.get("name", None) is None:
        msg = msg + "Name\n"

    if state.get("phone", None) is None:
        msg = msg + "Phone\n"

    if state.get("date_of_birth", None) is None:
        msg = msg + "Date of Birth"

    state["answer"] = msg
    state["stop"] = True
    return state

def react_node(state: State) -> State:
    response = ReactAgent.run(state["input"])
    try:
        response = json.loads(response)
    except:
        pass
    state["answer"] = response
    return state

graph_builder = StateGraph(State)

graph_builder.add_node("check_auth", check_auth)
graph_builder.add_node("react", react_node)

graph_builder.add_edge(START, "check_auth")
graph_builder.add_conditional_edges(
    "check_auth",
    path=lambda state: state.get("stop", False),
    path_map={
        False: "react",
        True: END
    }
)
graph_builder.add_edge("react", END)

graph = graph_builder.compile()

