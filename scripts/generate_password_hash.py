
from getpass import getpass
from pwdlib import PasswordHash

hasher = PasswordHash.recommended()

username = input("Identifiant : ").strip()
password = getpass("Mot de passe : ")

if not username or len(username) > 100:
    raise SystemExit("Identifiant invalide")

if len(password) < 12:
    raise SystemExit("Utilise au moins 12 caractères")

print(f"{username}={hasher.hash(password)}")
