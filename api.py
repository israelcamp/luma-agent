from typing import Union, Optional
import uuid

from fastapi import FastAPI
from pydantic import BaseModel
from sqlmodel import select

from src.db.db import init_db, create_db_and_tables, SessionDep
from src.db.models import Appointments
from src.graph import State, graph

class Message(BaseModel):
    input: str
    user_id: uuid.UUID
    session_id: Optional[uuid.UUID]

FAKE_REDIS = {}

app = FastAPI()

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.get("/appointments")
def read_appointments(session: SessionDep) -> list[Appointments]:
    return session.exec(select(Appointments)).all()

@app.post("/appointments")
def create_appointments(session: SessionDep):
    appointments = init_db(session)
    return {
        "user_id": appointments[-1].user_id,
    }

@app.post("/chat")
def chat(message: Message, session: SessionDep):
    user_id = message.user_id
    session_id = message.session_id

    appointments = session.exec(
        select(Appointments).where(Appointments.user_id == user_id)
    ).all()

    if session_id is None or session_id not in FAKE_REDIS:
        session_id = session_id or str(uuid.uuid4())
        FAKE_REDIS[session_id] = {
            "state": State(authenticated=False),
        }

    session_data = FAKE_REDIS[session_id]
    state = session_data["state"]
    state.update({
        "input": message.input,
        "appointments": appointments
    })

    response = graph.invoke(state)
    answer = response.pop("answer")
    appointments = response.pop("appointments")

    state.update(response)
    state.update({"stop": False, "input": None})

    for apt in appointments:
        session.add(apt)
    session.commit()

    FAKE_REDIS[session_id] = {
        "state": state,
    }
    return {
        "session_id": session_id,
        "answer": answer
    }
