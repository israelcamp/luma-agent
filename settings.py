from pydantic import BaseModel

class Settings(BaseModel):
    model: str = "llama3.1:8b-instruct-q4_K_M"

settings = Settings()
