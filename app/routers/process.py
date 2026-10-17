from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.auth.dependencies import CurrentUser

router = APIRouter()


class RequestData(BaseModel):
    nombre: float


# Ton endpoint de traitement est protégé.
@router.post("/process")
def process(
    data: RequestData,
    username: CurrentUser,
):
    return {"resultat": data.nombre * 2}
