
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


# Modèle des données reçues
class RequestData(BaseModel):
    message: str


# Vérifier que l'API fonctionne
@app.get("/")
def home():
    return {"status": "ok", "message": "API opérationnelle"}


# Recevoir une requête et retourner un résultat
@app.post("/process")
def process(data: RequestData):
    result = {
        "received": data.message,
        "result": f"Traitement effectué : {data.message}"
    }

    return result
