import json
from textwrap import dedent

from pydantic import BaseModel
from langchain_ollama import ChatOllama

from src.settings import settings

class AuthInfo(BaseModel):
    name: str | None
    phone: str | None
    date_of_birth: str | None

class AuthLLM:

    # TODO: deal with name without surname
    @staticmethod
    def prompt() -> str:
        return dedent("""
        Your task is to collect 3 informations from the user input:
        Name, Phone and Date of Birth
        
        Your output should be in JSON format:
        {{
            "name": (collected name of the user),
            "phone": (collected phone of the user),
            "date_of_birth": (collected date of birth of the user in the format YYYY-MM-DD)
        }}
        """).strip()

    @staticmethod
    def chat(input: str) -> dict:
        llm = ChatOllama(
            model=settings.model,
            temperature=0
        )
        llm = llm.with_structured_output(AuthInfo)
        
        response = llm.invoke([
            ("system", AuthLLM.prompt()),
            ("human", input)
        ])
        return response

    @staticmethod
    def run(
        input: str
    ) -> dict:
        response = AuthLLM.chat(input)
        infos = response.dict()
        keep_infos = {}
        for key, value in infos.items():
            if value is not None and not value.lower() in ("none", "null") and len(value) > 0:
                keep_infos[key] = value
        return keep_infos
