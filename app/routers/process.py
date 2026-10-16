from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.auth.dependencies import CurrentUser

router = APIRouter()


class RequestData(BaseModel):
    message: str = Field(max_length=5000)


# Ton endpoint de traitement est protégé.
@router.post("/process")
def process(
    data: RequestData,
    username: CurrentUser,
):
    # Plus tard, ton appel à Modal ira ici.
    result = {
        "received": data.message,
        "result": f"Traitement effectué : {data.message}",
    }

    return result
