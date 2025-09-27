from typing import Union
import uuid

from fastapi import FastAPI
from pydantic import BaseModel

from db.db import init_db
from graph import State, graph

class Message(BaseModel):
    input: str
    session_id: str | None

FAKE_REDIS = {}

app = FastAPI()

@app.get("/")
def chat(message: Message):
    session_id = message.session_id
    if session_id is None or session_id not in FAKE_REDIS:
        db = init_db()
        session_id = session_id or str(uuid.uuid4())
        FAKE_REDIS[session_id] = {
            "state": State(appointments=db),
        }

    session_data = FAKE_REDIS[session_id]
    state = session_data["state"]
    state["input"] = message.input

    response = graph.invoke(state)
    answer = response.pop("answer")
    state.update(response)
    state.update({"stop": False, "input": None})

    FAKE_REDIS[session_id] = {
        "state": state
    }

    return {
        "session_id": session_id,
        "answer": answer
    }
