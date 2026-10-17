import os

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.auth.dependencies import CurrentUser

router = APIRouter()

MODAL_URL = os.environ["MODAL_API_URL"]
MODAL_TOKEN_ID = os.environ["MODAL_TOKEN_ID"]
MODAL_TOKEN_SECRET = os.environ["MODAL_TOKEN_SECRET"]


class RequestData(BaseModel):
    nombre: float


# Ton endpoint de traitement est protégé.
@router.post("/process")
async def process(
    data: RequestData,
    username: CurrentUser,
):
    headers = {
        "Modal-Key": MODAL_TOKEN_ID,
        "Modal-Secret": MODAL_TOKEN_SECRET,
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=180.0) as client:
            response = await client.post(
                MODAL_URL,
                headers=headers,
                json={"nombre": data.nombre},
            )
            response.raise_for_status()

    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Le service Modal a mis trop de temps à répondre.")
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Erreur du service Modal ({exc.response.status_code}).",
        )
    except httpx.RequestError:
        raise HTTPException(status_code=502, detail="Impossible de joindre le service Modal.")

    return {
        "received": data.nombre,
        "result": response.json(),
    }