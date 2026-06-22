import numpy as np

from app.embeddings import embedding_from_json


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    dot_product = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return float(dot_product / (norm_a * norm_b))


def rank_documents(query_embedding: np.ndarray, documents: list, top_k: int = 5) -> list:
    scored = []
    for doc in documents:
        doc_embedding = embedding_from_json(doc.embedding)
        score = cosine_similarity(query_embedding, doc_embedding)
        scored.append((doc, score))

    scored.sort(key=lambda pair: pair[1], reverse=True)

    return scored[:top_k]