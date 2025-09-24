from typing import Annotated

from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

from llms.auth import AuthLLM

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
    print(infos)
    for key, value in infos.items():
        if value is not None:
            state[key] = value

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

graph_builder = StateGraph(State)

graph_builder.add_node("check_auth", check_auth)

graph_builder.add_edge(START, "check_auth")
graph_builder.add_edge("check_auth", END)

graph = graph_builder.compile()

