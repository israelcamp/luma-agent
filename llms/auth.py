import json
from textwrap import dedent

from ollama import chat


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
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "phone": {"type": "string"},
                "date_of_birth": {"type": "string"},
            }
        }
        response = chat(
            model="llama3.2:3b-instruct-q5_K_M",
            format=schema,
            options={"temperature": 0},
            messages = [
                {"role": "system", "content": AuthLLM.prompt()},
                {"role": "user", "content": input}
            ]
        )
        return response

    @staticmethod
    def run(
        input: str
    ) -> dict:
        response = AuthLLM.chat(input)
        infos = json.loads(response.message.content)
        keep_infos = {}
        for key, value in infos.items():
            if not value.lower() in ("none", "null") and len(value) > 0:
                keep_infos[key] = value
        return keep_infos
