"""Lazy-loaded local embeddings for Qdrant (FastEmbed — no separate vector DB server)."""
from __future__ import annotations

import threading
from typing import List

_lock = threading.Lock()
_model = None


def _get_model():
    global _model
    with _lock:
        if _model is None:
            from fastembed import TextEmbedding

            _model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")
        return _model


def embed_texts(texts: List[str]) -> List[List[float]]:
    if not texts:
        return []
    model = _get_model()
    return [vector.tolist() for vector in model.embed(texts)]


def embed_query(text: str) -> List[float]:
    vecs = embed_texts([text])
    return vecs[0] if vecs else []
