from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import srsly


class Appointments:
    place: str
    doctor: str
    speciality: str
    date: str
    time: str
    address: str
    canceled: bool


def init_db() -> list[Appointments]:
    data_path = Path(__file__).parent / "data.json"
    data = srsly.read_json(data_path)
    appointments = []
    for apt in data:
        dt = datetime.fromisoformat(apt["date_time"])
        day = dt.date()
        time = dt.time()
        appointments.append(Appointments(
            place=apt["place"],
            doctor=apt["doctor"],
            address=apt["address"],
            speciality=apt["speciality"],
            date=day,
            time=time,
            canceled=False
        ))
    return appointments

