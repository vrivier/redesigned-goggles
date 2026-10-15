
from fastapi import FastAPI
from pydantic import BaseModel

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")


# Modèle des données reçues
class RequestData(BaseModel):
    message: str


@app.get("/", include_in_schema=False)
async def home():
    return FileResponse("static/index.html")


# Recevoir une requête et retourner un résultat
@app.post("/process")
def process(data: RequestData):
    result = {
        "received": data.message,
        "result": f"Traitement effectué : {data.message}"
    }

    return result
