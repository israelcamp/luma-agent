from textwrap import dedent

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
    def run(
        name: str | None = None,
        phone: str | None = None,
        date_of_birth: str | None = None
    ) -> dict:
        return {
            "name": "Israel Campiotti",
            "phone": "+55 19 91234-5678",
            "date_of_birth": "1792-11-28"
        }
