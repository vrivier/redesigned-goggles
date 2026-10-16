import secrets

from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from pwdlib import PasswordHash

from app.config import APP_USERS, SESSION_MAX_AGE, SESSION_SECRET

serializer = URLSafeTimedSerializer(
    SESSION_SECRET,
    salt="app-session-v1",
)
password_hasher = PasswordHash.recommended()

# Hash factice pour limiter les différences de temps de réponse
# entre un utilisateur inconnu et un mot de passe incorrect.
DUMMY_HASH = password_hasher.hash(secrets.token_urlsafe(32))


def verify_credentials(username: str, password: str) -> bool:
    stored_hash = APP_USERS.get(username, DUMMY_HASH)

    try:
        valid_password = password_hasher.verify(password, stored_hash)
    except (ValueError, TypeError):
        valid_password = False

    return valid_password and username in APP_USERS


def create_session_token(username: str) -> str:
    return serializer.dumps({"sub": username})


def read_session_token(token: str) -> dict | None:
    """Retourne le contenu du token, ou None s'il est invalide ou expiré."""
    try:
        return serializer.loads(token, max_age=SESSION_MAX_AGE)
    except (BadSignature, SignatureExpired):
        return None
