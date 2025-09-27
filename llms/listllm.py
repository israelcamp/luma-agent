from textwrap import dedent

from langchain_ollama import ChatOllama
from pydantic import BaseModel

from db.db import Appointments
from settings import settings


class ChosenAppointments(BaseModel):
    ids: list[int]


class ListLLM:

    @staticmethod
    def prompt() -> str:
        return dedent(
            """
        You will receive a list of appointments and a user message.
        Your task is to return the ids of the Appointments that are related to the user message.

        For example, the user might ask for appointments in a specific date, in that case you should return only the IDs from the appointments that are scheduled for that day.
        If given only a date you should return the appointments for that date.

        Your response should be in a JSON format:
        {{
            "ids": (list of integers ids of the relevant appointments)
        }}
        """
        )

    @staticmethod
    def list_of_appointments(appointments: list[Appointments]) -> str:
        texts = []
        for apt in appointments:
            text = dedent(
                f"""
            Appointment ID: {apt.id}
            Speciality: {apt.speciality}
            Schedule for: {apt.date} at {apt.time}
            Is confirmed? {apt.confirmed}
            """
            ).strip()
            texts.append(text)
        return "\n\n".join(
            ["== LIST OF APPOINTMENTS ==", *texts, "== END OF LIST OF APPOINTMENTS =="]
        )

    @staticmethod
    def chat(input: str, appointments: list[Appointments]) -> dict:
        llm = ChatOllama(model=settings.model, temperature=0)
        llm = llm.with_structured_output(ChosenAppointments)

        appointments = ListLLM.list_of_appointments(appointments)
        message = f"{appointments}\nUser Message: {input}"

        response = llm.invoke([("system", ListLLM.prompt()), ("human", message)])
        return response

    @staticmethod
    def run(input: str, appointments: list[Appointments]) -> str:
        response = ListLLM.chat(input, appointments)
        return response.ids
