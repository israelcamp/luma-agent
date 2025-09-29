from datetime import datetime
from pathlib import Path
from uuid import uuid4
from typing import Annotated

from fastapi import Depends
import srsly
from sqlmodel import Field, Session, SQLModel, create_engine, select

from src.settings import settings
from src.db.models import Appointments

engine = create_engine(
    f"sqlite:///{settings.sqlite_file_name}",
    connect_args = {
        "check_same_thread": False
    }
)

def init_db(session) -> list[Appointments]:
    data_path = Path(__file__).parent / "data.json"
    data = srsly.read_json(data_path)
    user_id = uuid4()
    appointments = []
    for i, apt in enumerate(data):
        dt = datetime.fromisoformat(apt["date_time"])
        day = dt.date().strftime("%d %B %Y")
        time = dt.time().strftime("%I:%M %p")
        appointments.append(Appointments(
            user_id=user_id,
            id=i,
            place=apt["place"],
            doctor=apt["doctor"],
            address=apt["address"],
            speciality=apt["speciality"],
            date=day,
            time=time,
            canceled=False,
            confirmed=False
        ))
        session.add(appointments[-1])
    session.commit()
    return appointments

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]
