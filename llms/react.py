from textwrap import dedent

from rich import print
from langchain.tools import tool
from langchain_ollama import ChatOllama

from db.db import Appointments
from llms.listllm import ListLLM
from react.react_agent import create_react_agent
from settings import settings


def create_list_appointments_tool(input: str, appointments: list[Appointments]):
    @tool
    def list_appointments() -> list[dict]:
        """
        Lists all appointments that are not canceled
        This tool should be used whenever the user asks:
        To see his appoints, check futures appointments, wants to know unconfirmed appoints and so on.

        Examples:
        What are my appointments for the next week?
        Do I have an appointment with cardiologist?
        """
        ids = ListLLM.run(input)
        texts = []
        for apt in appointments:
            if apt.id not in ids:
                continue

            text = dedent(
                f"""
            Appointment ID: {apt.id} (appointment_id)
            Doctor name: {apt.doctor}
            Speciality: {apt.speciality}
            Schedule for: {apt.date} at {apt.time}
            Is confirmed? {apt.confirmed}
            """
            ).strip()
            texts.append(text)
        return "\n\n".join(
            ["== LIST OF APPOINTMENTS ==", *texts, "== END OF LIST OF APPOINTMENTS =="]
        )

    return list_appointments

def create_confirm_tool(appointments: list[Appointments]):
    @tool
    def confirm_appointment(appointment_id:  int) -> str:
        """
        This tool should be used to confirm appointments using their id
        The appointments first need to be listed than the ID should be used to confirm
        """
        for apt in appointments:
            if apt.id == appointment_id:
                apt.confirmed = True
                return f"Appointment with id {appointment_id} confirmed!"
        return f"No appointment with id {appointment_id} was found"
    return confirm_appointment

def create_cancel_tool(appointments: list[Appointments]):
    @tool
    def cancel_appointment(appointment_id:  int) -> str:
        """
        This tool should be used to cancel appointments using their id
        The appointments first need to be listed than the ID should be used to cancel
        """
        for apt in appointments:
            if apt.id == appointment_id:
                apt.confirmed = False
                apt.canceled = True
                return f"Appointment with id {appointment_id} is canceled!"
        return f"No appointment with id {appointment_id} was found"
    return cancel_appointment

@tool
def greeting() -> str:
    """This tool should be used when the user sends a message containing only their personal information, like Name, Phone and Date of Birth"""
    return dedent(
        """
    Hello! Tell me if you want to list, cancel or confirm your appointments.
    """
    ).strip()


class ReactAgent:

    @staticmethod
    def prompt() -> str:
        return dedent(
            """
        The user will send you a message, you should check if you have any tool available that can help you answer the message correctly.

        In the case that the user gives you a message containing only their personal information, you should call the appropriate tool "greeting".
        IMPORTANT: The message from this tool should be returned to the user.

        When listing the appointments to the user, DO NOT show the ID.
        
        If the user asks to confirm an appointment you should first list the related appointments then use the "confirm_appointment" tool passig the ID as parameter.
            For example, if the user asks to confirm an appointment for an specific day you should first list the appointments then give the correct ID to the "confirm_appointment" tool.
        """
        )

    @staticmethod
    def run(input: str, appointments: list[Appointments]) -> str:
        llm = ChatOllama(model=settings.model, temperature=0)
        tools = [
            greeting,
            create_list_appointments_tool(input, appointments),
            create_confirm_tool(appointments),
            create_cancel_tool(appointments)
        ]

        agent = create_react_agent(
            llm, tools=tools, prompt=ReactAgent.prompt(), # stop_tools=["greeting"]
        )

        response = agent.invoke({"messages": [("user", input)]})
        print(response)
        answer = response["messages"][-1].content
        return answer
