from pydantic import BaseModel

class Settings(BaseModel):
    # NOTE: llama3.1:8b-instruct-q4_K_M could also be used for larger model
    model: str = "llama3.2:3b-instruct-q5_K_M"
    max_history: int = 2

settings = Settings()
