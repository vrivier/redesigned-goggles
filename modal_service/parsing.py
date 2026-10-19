import json
from json import JSONDecoder

ANSWER_KEYS = ("best_move_uci", "move_source", "raw_text")

decoder = JSONDecoder()


def extract_answer(*outputs: str) -> dict | None:
    """Retourne le dernier objet JSON reconnu comme réponse de Queen, ou None."""
    answer = None
    for output in outputs:
        for i, ch in enumerate(output):
            if ch != "{":
                continue
            try:
                value, _ = decoder.raw_decode(output[i:])
            except json.JSONDecodeError:
                continue
            if isinstance(value, dict) and any(k in value for k in ANSWER_KEYS):
                answer = value
    return answer
