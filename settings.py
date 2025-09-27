from pydantic import BaseModel

class Settings(BaseModel):
    # model: str = "llama3.1:8b-instruct-q4_K_M"
    model: str = "llama3.2:3b-instruct-q5_K_M"
    max_history: int = 2

settings = Settings()
