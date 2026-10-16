from typing import Annotated

from fastapi import Depends, HTTPException, Request

from app.auth.security import read_session_token
from app.config import APP_ORIGIN, APP_USERS, COOKIE_NAME


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

    session = read_session_token(token)

    if session is None:
        raise HTTPException(
            status_code=401,
            detail="Session invalide ou expirée",
        )

    username = session.get("sub")

    # Retirer l'accès si l'utilisateur n'est plus autorisé
    # dans la configuration Render.
    if not isinstance(username, str) or username not in APP_USERS:
        raise HTTPException(
            status_code=401,
            detail="Utilisateur non autorisé",
        )

    return username


CurrentUser = Annotated[str, Depends(get_current_user)]
