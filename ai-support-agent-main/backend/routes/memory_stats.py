from typing import Any, Dict, List

from fastapi import APIRouter, Depends
from qdrant_client.http import models as qm
from sqlalchemy.orm import Session

from config.settings import settings
from database.db import get_db
from database.models import Conversation, Message, User
from deps import get_current_user
from services.memory_analytics import efficacy_summary, sentiment_trajectory
from services.qdrant_service import get_client, search_similar

router = APIRouter(prefix="/memory", tags=["memory"])


@router.get("/overview")
def memory_overview(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    convs = db.query(Conversation).filter(Conversation.user_id == user.id).order_by(Conversation.updated_at.desc()).limit(20).all()
    total_messages = (
        db.query(Message)
        .join(Conversation)
        .filter(Conversation.user_id == user.id)
        .count()
    )
    points = 0
    try:
        client = get_client()
        flt = qm.Filter(must=[qm.FieldCondition(key="user_id", match=qm.MatchValue(value=user.id))])
        scroll, _ = client.scroll(
            collection_name=settings.collection_name,
            scroll_filter=flt,
            limit=512,
            with_payload=False,
            with_vectors=False,
        )
        points = len(scroll)
    except Exception:
        points = 0

    return {
        "user": {
            "id": user.id,
            "display_name": user.display_name,
            "memory_consent": user.memory_consent,
        },
        "conversations": len(convs),
        "messages_indexed_estimate": points,
        "total_messages": total_messages,
        "efficacy": efficacy_summary(db, user.id),
    }


@router.get("/graph")
def memory_graph_data(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """Lightweight 'knowledge graph' view: conversations as nodes linked by shared channel + recency."""
    convs = (
        db.query(Conversation)
        .filter(Conversation.user_id == user.id)
        .order_by(Conversation.updated_at.desc())
        .limit(40)
        .all()
    )
    nodes: List[Dict[str, Any]] = []
    edges: List[Dict[str, Any]] = []
    for c in convs:
        nodes.append(
            {
                "id": f"c{c.id}",
                "label": c.title or f"Chat {c.id}",
                "type": "conversation",
                "channel": c.channel,
                "updated_at": c.updated_at.isoformat() if c.updated_at else None,
            }
        )
    for i in range(len(convs) - 1):
        a, b = convs[i], convs[i + 1]
        if a.channel == b.channel:
            edges.append({"source": f"c{a.id}", "target": f"c{b.id}", "kind": "same_channel_sequence"})
        else:
            edges.append({"source": f"c{a.id}", "target": f"c{b.id}", "kind": "cross_channel_handoff"})

    return {"nodes": nodes, "edges": edges}


@router.get("/trajectory/{conversation_id}")
def trajectory(
    conversation_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    conv = db.query(Conversation).filter(Conversation.id == conversation_id, Conversation.user_id == user.id).first()
    if not conv:
        return {"error": "not_found"}
    return {"conversation_id": conversation_id, "trajectory": sentiment_trajectory(db, conversation_id)}


@router.post("/probe")
def semantic_probe(
    payload: Dict[str, str],
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    q = (payload.get("query") or "").strip()
    if not q:
        return {"hits": []}
    hits = search_similar(user.id, q, limit=8) if user.memory_consent else []
    return {"hits": hits}
