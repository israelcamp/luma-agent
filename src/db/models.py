import uuid

from sqlmodel import Field, SQLModel


class Appointments(SQLModel, table=True):
    appointment_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    user_id: uuid.UUID
    id: int | None
    place: str
    doctor: str
    speciality: str
    date: str
    time: str
    address: str
    canceled: bool = False
    confirmed: bool = False


