# Queen – API d'analyse d'échecs

Petite application web qui analyse une position d'échecs (au format FEN) avec le modèle [`princeton-nlp/queen_hce-4`](https://huggingface.co/princeton-nlp/queen_hce-4).

Elle se compose de deux parties :

- **Une API FastAPI** (`main.py`, `app/`) : sert l'interface web, gère l'authentification par session et relaie les requêtes vers Modal. Prévue pour être déployée sur Render.
- **Un service d'inférence Modal** (`modal_service/`) : exécute le modèle Queen sur un GPU H100 et renvoie la réponse en JSON.

```
Navigateur ──► FastAPI (Render) ──► Modal (endpoint CPU) ──► Modal (GPU H100, Queen)
  static/        /api/login            infer()                  run_queen()
  index.html     /process
```

## Structure du projet

```
main.py                       Point d'entrée FastAPI (routes, fichiers statiques)
app/
  config.py                   Variables d'environnement, paramètres de cookie
  auth/                       Login/logout, sessions signées, contrôle d'origine
  routers/process.py          POST /process : appelle le service Modal
modal_service/
  config.py                   Image Modal, modèle, prompt par défaut
  modal_app.py                Endpoint HTTP (CPU), protégé par proxy auth
  queen.py                    Fonction GPU qui lance l'inférence
  parsing.py                  Extraction du JSON de réponse
  schemas.py                  Schéma de requête (fen, prompt)
scripts/generate_password_hash.py   Génère le hash d'un mot de passe utilisateur
static/index.html             Interface web
```

## Prérequis

- Python 3.12
- Un compte [Modal](https://modal.com) avec un token d'API
- (Déploiement) un service web Render

## Installation

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows  (source .venv/bin/activate sur Linux/macOS)
pip install -r requirements.txt
```

## Déployer le service Modal

```bash
modal setup                                   # première fois seulement
modal deploy modal_service/modal_app.py
```

La commande affiche l'URL de l'endpoint `infer` : c'est la valeur de `MODAL_API_URL`.
Pour créer les tokens d'authentification du proxy (`Modal-Key` / `Modal-Secret`), voir *Settings → Proxy Auth Tokens* dans Modal.

## Configuration de l'API

Toutes les variables suivantes sont **obligatoires** (l'application ne démarre pas sans elles) :

| Variable             | Description                                                              |
|----------------------|--------------------------------------------------------------------------|
| `SESSION_SECRET`     | Secret utilisé pour signer les cookies de session                        |
| `APP_USERS_JSON`     | Utilisateurs autorisés, en JSON : `{"identifiant": "hash_du_mot_de_passe"}` |
| `APP_ORIGIN`         | Origine publique de l'app (ex. `https://mon-app.onrender.com`)           |
| `MODAL_API_URL`      | URL de l'endpoint Modal `infer`                                          |
| `MODAL_TOKEN_ID`     | Identifiant du token de proxy auth Modal                                 |
| `MODAL_TOKEN_SECRET` | Secret du token de proxy auth Modal                                      |

### Créer un utilisateur

```bash
python scripts/generate_password_hash.py
```

Le script affiche une ligne `identifiant=hash` (mot de passe de 12 caractères minimum). Placez le hash dans `APP_USERS_JSON`.

## Lancer en local

```bash
uvicorn main:app --reload
```

L'interface est disponible sur http://localhost:8000.

> Le cookie de session est `Secure` (préfixe `__Host-`) et `APP_ORIGIN` est vérifié au login : en local, `APP_ORIGIN` doit correspondre à l'URL utilisée, et certains navigateurs n'acceptent les cookies `Secure` que sur `localhost` ou en HTTPS.

## Endpoints

| Méthode | Route         | Auth | Description                                          |
|---------|---------------|------|------------------------------------------------------|
| GET     | `/`           | non  | Interface web                                        |
| POST    | `/api/login`  | non  | Connexion (`username`, `password`), pose le cookie   |
| GET     | `/api/me`     | oui  | Utilisateur courant                                  |
| POST    | `/api/logout` | non  | Déconnexion                                          |
| POST    | `/process`    | oui  | Analyse d'une position                               |

### `POST /process`

```json
{
  "message": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
  "question": "Quel est le meilleur coup ?"
}
```

- `message` : la position au format FEN (obligatoire)
- `question` : prompt personnalisé (optionnel, sinon un prompt d'analyse par défaut est utilisé)

La réponse contient `received` (la FEN envoyée) et `result` (la réponse JSON de Queen, par ex. `best_move_uci`).

## Sécurité

- Mots de passe hachés avec Argon2 (`pwdlib`)
- Session dans un cookie signé, `HttpOnly`, `Secure`, `SameSite=Lax`, durée 8 h
- Vérification de l'origine sur les routes de login/logout
- L'endpoint Modal est protégé par proxy auth ; les identifiants ne quittent jamais le serveur

## Images

<img width="726" height="526" alt="Capture d&#39;écran 2026-11-19 175455" src="https://github.com/user-attachments/assets/b9f155b7-da4c-4a6c-8f72-abc8577b89ef" />
<img width="725" height="571" alt="Capture d&#39;écran 2026-11-19 175511" src="https://github.com/user-attachments/assets/8165ef4e-4730-4eed-8249-6d48cd4b761f" />
