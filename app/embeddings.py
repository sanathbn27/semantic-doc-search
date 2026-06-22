import json

import numpy as np
from sentence_transformers import SentenceTransformer

_model = SentenceTransformer("all-MiniLM-L6-v2")


def encode(text: str) -> np.ndarray:
    return _model.encode(text)


def embedding_to_json(embedding: np.ndarray) -> str:
    return json.dumps(embedding.tolist())


def embedding_from_json(embedding_json: str) -> np.ndarray:
    return np.array(json.loads(embedding_json))