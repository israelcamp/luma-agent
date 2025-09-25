from textwrap import dedent

from langchain.tools import tool
from langchain_ollama import ChatOllama

from db.db import db
from react.react_agent import create_react_agent


@tool
def list_appointments() -> list[dict]:
    """Lists all appointments that are not canceled"""
    return [v.dict() for v in db]


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
        
        """
        )

    @staticmethod
    def run(input: str) -> str:
        llm = ChatOllama(model="llama3.2:3b-instruct-q5_K_M")
        tools = [list_appointments, greeting]

        agent = create_react_agent(
            llm, tools=tools, prompt=ReactAgent.prompt(), stop_tools=["greeting"]
        )

        response = agent.invoke({"messages": [("user", input)]})
        answer = response["messages"][-1].content
        return answer
