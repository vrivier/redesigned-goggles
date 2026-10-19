import modal

MODEL_ID = "princeton-nlp/queen_hce-4"
MODEL_DIR = "/opt/queen"
DEFAULT_PROMPT = "Analyse la position échiquéenne donnée, \
    identifie le meilleur coup, indique la variante critique \
    en supposant un jeu optimal, liste les coups prometteurs \
    méritant un examen plus approfondi, et évalue la position."  

# Modules locaux à embarquer dans les conteneurs (Modal ne le fait pas automatiquement).
LOCAL_MODULES = ("config", "schemas", "parsing", "queen")

app = modal.App("queen-hce-inference")

gpu_image = (
    modal.Image.debian_slim(python_version="3.12")
    .uv_pip_install("uv", "huggingface-hub==1.27.0")
    .run_commands(
        f"hf download {MODEL_ID} --local-dir {MODEL_DIR}",
        f"uv pip sync --system {MODEL_DIR}/requirements-inference.txt",
    )
    .add_local_python_source(*LOCAL_MODULES)
)

web_image = (
    modal.Image.debian_slim(python_version="3.12")
    .uv_pip_install("fastapi[standard]")
    .add_local_python_source(*LOCAL_MODULES)
)
