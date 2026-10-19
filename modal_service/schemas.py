from pydantic import BaseModel


class InferRequest(BaseModel):
    fen: str
    prompt: str | None = None
