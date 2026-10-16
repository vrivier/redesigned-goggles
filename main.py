
import hashlib
import json
import os
import secrets
from pathlib import Path
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from pydantic import BaseModel, Field
from pwdlib import PasswordHash

app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

app.mount(
    "/static",
    StaticFiles(directory=str(STATIC_DIR)),
    name="static",
)

# Configuration obligatoire dans les variables d'environnement Render.
SESSION_SECRET = os.environ["SESSION_SECRET"]
APP_USERS = json.loads(os.environ["APP_USERS_JSON"])
APP_ORIGIN = os.environ["APP_ORIGIN"].rstrip("/")

COOKIE_NAME = "__Host-session"
SESSION_MAX_AGE = 8 * 60 * 60  # 8 heures

serializer = URLSafeTimedSerializer(
    SESSION_SECRET,
    salt="app-session-v1",
)
password_hasher = PasswordHash.recommended()

# Hash factice pour limiter les différences de temps de réponse
# entre un utilisateur inconnu et un mot de passe incorrect.
DUMMY_HASH = password_hasher.hash(secrets.token_urlsafe(32))


class RequestData(BaseModel):
    message: str = Field(max_length=5000)


class LoginData(BaseModel):
    username: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=1, max_length=256)


def require_same_origin(request: Request):
    # Défense CSRF pour les requêtes qui modifient l'état.
    origin = request.headers.get("origin")

    if not origin or origin.rstrip("/") != APP_ORIGIN:
        raise HTTPException(
            status_code=403,
            detail="Origine non autorisée",
        )


def get_current_user(request: Request) -> str:
    token = request.cookies.get(COOKIE_NAME)

    if not token:
        raise HTTPException(
            status_code=401,
            detail="Connexion requise",
        )

    try:
        session = serializer.loads(
            token,
            max_age=SESSION_MAX_AGE,
        )
        username = session.get("sub")

    except (BadSignature, SignatureExpired):
        raise HTTPException(
            status_code=401,
            detail="Session invalide ou expirée",
        )

    # Retirer l'accès si l'utilisateur n'est plus autorisé
    # dans la configuration Render.
    if not isinstance(username, str) or username not in APP_USERS:
        raise HTTPException(
            status_code=401,
            detail="Utilisateur non autorisé",
        )

    return username


CurrentUser = Annotated[str, Depends(get_current_user)]


@app.get("/", include_in_schema=False)
async def home():
    return FileResponse(STATIC_DIR / "index.html")


@app.post("/api/login")
def login(
    data: LoginData,
    request: Request,
    response: Response,
):
    require_same_origin(request)

    stored_hash = APP_USERS.get(data.username, DUMMY_HASH)

    try:
        valid_password = password_hasher.verify(
            data.password,
            stored_hash,
        )
    except (ValueError, TypeError):
        valid_password = False

    if not valid_password or data.username not in APP_USERS:
        raise HTTPException(
            status_code=401,
            detail="Identifiant ou mot de passe incorrect",
        )

    token = serializer.dumps({"sub": data.username})

    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        max_age=SESSION_MAX_AGE,
        httponly=True,
        secure=True,
        samesite="lax",
        path="/",
    )

    return {"ok": True}


@app.get("/api/me")
def me(username: CurrentUser):
    return {"username": username}


@app.post("/api/logout")
def logout(
    request: Request,
    response: Response,
):
    require_same_origin(request)

    response.delete_cookie(
        key=COOKIE_NAME,
        path="/",
        secure=True,
        httponly=True,
        samesite="lax",
    )

    return {"ok": True}


# Ton endpoint de traitement est protégé.
@app.post("/process")
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
