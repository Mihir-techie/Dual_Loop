from __future__ import annotations

import uuid
from pathlib import Path
from typing import Any, Dict, List

from qdrant_client import QdrantClient
from qdrant_client.http import models as qm

from config.settings import settings
from services.embedding_service import embed_query, embed_texts

_VECTOR_SIZE = 384
_client: QdrantClient | None = None


def get_client() -> QdrantClient:
    global _client
    if _client is None:
        path = (settings.qdrant_path or "").strip()
        if path and path != ":memory:":
            Path(path).mkdir(parents=True, exist_ok=True)
            _client = QdrantClient(path=path)
        else:
            _client = QdrantClient(":memory:")
        _ensure_collection(_client)
    return _client


def _ensure_collection(client: QdrantClient) -> None:
    cols = {c.name for c in client.get_collections().collections}
    if settings.collection_name not in cols:
        client.create_collection(
            collection_name=settings.collection_name,
            vectors_config=qm.VectorParams(size=_VECTOR_SIZE, distance=qm.Distance.COSINE),
        )


def upsert_memory_point(
    user_id: int,
    conversation_id: int,
    message_id: int,
    document: str,
    payload: Dict[str, Any],
) -> str:
    client = get_client()
    point_id = str(uuid.uuid5(uuid.NAMESPACE_URL, f"{user_id}:{message_id}"))
    vector = embed_texts([document])[0]
    client.upsert(
        collection_name=settings.collection_name,
        points=[
            qm.PointStruct(
                id=point_id,
                vector=vector,
                payload={
                    "user_id": user_id,
                    "conversation_id": conversation_id,
                    "message_id": message_id,
                    "text": document[:8000],
                    **payload,
                },
            )
        ],
    )
    return point_id


def search_similar(
    user_id: int,
    query: str,
    limit: int = 6,
) -> List[Dict[str, Any]]:
    client = get_client()
    vector = embed_query(query)
    query_filter = qm.Filter(
        must=[qm.FieldCondition(key="user_id", match=qm.MatchValue(value=user_id))]
    )
    hits = client.search(
        collection_name=settings.collection_name,
        query_vector=vector,
        query_filter=query_filter,
        limit=limit,
        with_payload=True,
    )
    results: List[Dict[str, Any]] = []
    for h in hits:
        p = h.payload or {}
        results.append(
            {
                "score": float(h.score),
                "text": p.get("text"),
                "conversation_id": p.get("conversation_id"),
                "sentiment": p.get("sentiment"),
                "channel": p.get("channel"),
                "created_at": p.get("created_at"),
            }
        )
    return results
