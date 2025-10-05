from textwrap import dedent

from rich import print
from langchain.tools import tool
from langchain_ollama import ChatOllama
from langchain_core.messages import BaseMessage
from langgraph.prebuilt import create_react_agent

from src.db.db import Appointments
from src.settings import settings


class ReactAgent:
    def create_confirm_tool(self, appointments: list[Appointments]):
        @tool
        def confirm_appointment(
            appointment_ids: list[int],
        ) -> str:
            """
            This tool should be used to confirm appointments using their appointment_id
            To be used only for messages such as:
            - Confirm my appointments
            - Confirm appointment with doctor John
            - Confirm appointment for december 12
            """
            confirmed = []
            for apt in appointments:
                if apt.id in appointment_ids:
                    apt.confirmed = True
                    text = dedent(
                        f"""
                    Appointment with appointment_id {apt.id} confirmed!
                    """
                    ).strip()
                    confirmed.append(text)
            if len(confirmed):
                msg = "\n\n".join(confirmed)
            else:
                msg = "No appointments were found"
            return msg

        return confirm_appointment

    def create_cancel_tool(self, appointments: list[Appointments]):
        @tool
        def cancel_appointment(appointment_ids: list[int]) -> str:
            """
            This tool should be used to cancel appointments using their appointment_id
            """
            canceled = []
            for apt in appointments:
                if apt.id in appointment_ids:
                    apt.confirmed = False
                    apt.canceled = True
                    text = dedent(
                        f"""
                    Appointment with appointment_id {apt.id} canceled.
                    """
                    ).strip()

                    canceled.append(text)
            if len(canceled):
                msg = "\n\n".join(canceled)
            else:
                msg = "No appointments were found"
            return msg

        return cancel_appointment

    @staticmethod
    def prompt(appointments: list[Appointments]) -> str:
        texts = []
        for apt in appointments:
            text = dedent(
                f"""
            appointment_id: {apt.id}
            - Doctor name: {apt.doctor}
            - Speciality: {apt.speciality}
            - Schedule for: {apt.date} at {apt.time}
            - Is confirmed? {apt.confirmed}
            - Is canceled? {apt.canceled}
            """
            ).strip()
            texts.append(text)

        appointments_text = "\n\n".join(
            ["== LIST OF APPOINTMENTS ==", *texts, "== END OF LIST OF APPOINTMENTS =="]
        )

        return dedent(
            f"""
        The user will send you a message, you should check if you have any tool available that can help you answer the message correctly.

        {appointments_text}

        When the user wants to confirm or cancel an appointment you should call "confirm_appointment" or "cancel_appointment" with the correct appointment_ids.

        After calling and/or using the tools "confirm_appointment", "cancel_appointment" you should inform the result.
        """
        )

    def run(
        self, input: str, history: list[BaseMessage], appointments: list[Appointments]
    ) -> str:
        llm = ChatOllama(model=settings.model, temperature=0)
        tools = [
            self.create_cancel_tool(appointments),
            self.create_confirm_tool(appointments),
        ]

        agent = create_react_agent(
            llm, tools=tools, prompt=ReactAgent.prompt(appointments)
        )

        response = agent.invoke({"messages": history + [("user", input)]})
        print(response)
        answer = response["messages"][-1].content
        return answer
