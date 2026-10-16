import json
import os

# Configuration obligatoire dans les variables d'environnement Render.
SESSION_SECRET = os.environ["SESSION_SECRET"]
APP_USERS = json.loads(os.environ["APP_USERS_JSON"])
APP_ORIGIN = os.environ["APP_ORIGIN"].rstrip("/")

COOKIE_NAME = "__Host-session"
SESSION_MAX_AGE = 8 * 60 * 60  # 8 heures
