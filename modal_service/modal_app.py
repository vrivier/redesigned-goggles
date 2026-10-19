import modal

from config import DEFAULT_PROMPT, app, web_image
from queen import run_queen
from schemas import InferRequest


# --- CPU : reçoit toutes les requêtes HTTP, y compris les invalides ---
@app.function(image=web_image)
@modal.fastapi_endpoint(method="POST", requires_proxy_auth=True, docs=True)
def infer(req: InferRequest) -> dict:
    prompt = req.prompt if req.prompt is not None else DEFAULT_PROMPT
    return run_queen.remote(req.fen, prompt)
