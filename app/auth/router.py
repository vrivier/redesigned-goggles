from fastapi import APIRouter, HTTPException, Request, Response

from app.auth.dependencies import CurrentUser, require_same_origin
from app.auth.schemas import LoginData
from app.auth.security import create_session_token, verify_credentials
from app.config import COOKIE_NAME, SESSION_MAX_AGE

router = APIRouter(prefix="/api")


@router.post("/login")
def login(
    data: LoginData,
    request: Request,
    response: Response,
):
    require_same_origin(request)

    if not verify_credentials(data.username, data.password):
        raise HTTPException(
            status_code=401,
            detail="Identifiant ou mot de passe incorrect",
        )

    response.set_cookie(
        key=COOKIE_NAME,
        value=create_session_token(data.username),
        max_age=SESSION_MAX_AGE,
        httponly=True,
        secure=True,
        samesite="lax",
        path="/",
    )

    return {"ok": True}


@router.get("/me")
def me(username: CurrentUser):
    return {"username": username}


@router.post("/logout")
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
