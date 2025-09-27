from typing import Union, Optional
import uuid

from fastapi import FastAPI
from pydantic import BaseModel

from src.db.db import init_db
from src.graph import State, graph

class Message(BaseModel):
    input: str
    session_id: Optional[str]

FAKE_REDIS = {}

app = FastAPI()

@app.post("/")
def chat(message: Message):
    session_id = message.session_id
    if session_id is None or session_id not in FAKE_REDIS:
        appointments = init_db()
        session_id = session_id or str(uuid.uuid4())
        FAKE_REDIS[session_id] = {
            "state": State(authenticated=False),
            "appointments": appointments
        }
    # NOTE: For real project the appointments would be stored in database with proper CRUD.
    # NOTE: The state could still be saved in Redis for fast retrieval.

    session_data = FAKE_REDIS[session_id]
    state = session_data["state"]
    state.update({
        "input": message.input,
        "appointments": session_data["appointments"]
    })

    response = graph.invoke(state)
    answer = response.pop("answer")
    appointments = response.pop("appointments")

    state.update(response)
    state.update({"stop": False, "input": None})

    FAKE_REDIS[session_id] = {
        "state": state,
        "appointments": appointments
    }

    return {
        "session_id": session_id,
        "answer": answer
    }
