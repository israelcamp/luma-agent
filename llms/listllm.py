from textwrap import dedent

from langchain_ollama import ChatOllama
from pydantic import BaseModel

from db.db import Appointments
from settings import settings


class ChosenAppointments(BaseModel):
    appointment_ids: list[int]


class ListLLM:

    @staticmethod
    def prompt() -> str:
        return dedent(
            """
        You will receive a list of appointments and a user message.
        Your task is to return the ids of the Appointments that are related to the user message.

        You should return the relevant appointments for the given query.
        For example, the query might be a specific date, in that case you should return only the IDs from the appointments that are scheduled for that day.
        If given only a date you should return the appointments for that date.

        Your response should be in a JSON format:
        {{
            "appointment_ids": (list of integers appointment_ids of the relevant appointments)
        }}
        """
        )

    @staticmethod
    def list_of_appointments(appointments: list[Appointments]) -> str:
        texts = []
        for apt in appointments:
            text = dedent(
                f"""
            appointment_id: {apt.id}
            - Date: {apt.date}
            - Time: {apt.time}
            - Speciality: {apt.speciality}
            - Is confirmed? {apt.confirmed}
            - Is canceled? {apt.canceled}
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
        message = f"{appointments}\n\nQuery: Give me appointments with {input}"

        response = llm.invoke([("system", ListLLM.prompt()), ("human", message)])
        return response

    @staticmethod
    def run(input: str, appointments: list[Appointments]) -> str:
        response = ListLLM.chat(input, appointments)
        return response.appointment_ids
