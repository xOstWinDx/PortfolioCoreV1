
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(
    title="Portfolio Backend",
    version="0.0.1",
    description="API for my portfolio website and blog."
)

class Message(BaseModel):
    message: str

@app.get("/", response_model=Message)
async def root() -> Message:
    return Message(message="Hello World")