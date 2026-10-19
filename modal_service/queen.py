import subprocess
import sys

from config import MODEL_DIR, app, gpu_image
from parsing import extract_answer


# --- GPU : appelée seulement quand la requête est déjà validée ---
@app.function(
    image=gpu_image,
    gpu="H100",
    timeout=180,
    scaledown_window=5,
    max_containers=1,
)
def run_queen(fen: str, prompt: str) -> dict:
    result = subprocess.run(
        [sys.executable, f"{MODEL_DIR}/infer.py", "--fen", fen, "--prompt", prompt],
        capture_output=True, text=True, timeout=180,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Queen a échoué.\n{result.stderr[-4000:]}")

    answer = extract_answer(result.stdout, result.stderr)
    if answer is None:
        raise RuntimeError(f"Pas de JSON reconnu.\n{result.stdout[-4000:]}")
    return answer
