"""Structured memory signals: sentiment trajectory, repeat attempts, efficacy hints."""
from __future__ import annotations

from collections import Counter
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

from database.models import Conversation, Message


FRUSTRATION_MARKERS = (
    "again",
    "still not",
    "still doesn't",
    "third time",
    "3rd time",
    "fourth time",
    "already tried",
    "nothing works",
    "useless",
    "escalate",
    "manager",
    "angry",
    "frustrated",
)


def _parse_sentiment_label(sentiment: Optional[str]) -> str:
    if not sentiment:
        return "unknown"
    s = sentiment.lower()
    if s in ("high", "negative", "angry"):
        return "high"
    if s in ("medium", "mixed"):
        return "medium"
    return "low"


def detect_sentiment_detailed(text: str) -> Tuple[str, float]:
    t = text.lower()
    score = 0.0
    if any(w in t for w in ("angry", "furious", "terrible", "worst", "lawsuit", "useless")):
        score += 0.45
    if any(w in t for w in ("frustrated", "annoyed", "ridiculous", "unacceptable", "again")):
        score += 0.25
    if any(w in t for w in ("not working", "doesn't work", "broken", "error", "failed")):
        score += 0.2
    if any(w in t for w in ("please", "thank", "appreciate", "great", "love")):
        score -= 0.15
    score = max(0.0, min(1.0, score + 0.05))  # slight baseline
    if score >= 0.55:
        label = "high"
    elif score >= 0.3:
        label = "medium"
    else:
        label = "low"
    return label, score


def thread_frustration_signals(messages: List[Message]) -> int:
    users = [m for m in messages if m.role == "user"]
    return sum(1 for m in users if any(marker in m.content.lower() for marker in FRUSTRATION_MARKERS))


def count_frustration_attempts(db: Session, user_id: int, conversation_id: int) -> int:
    conv_ids = [c.id for c in db.query(Conversation).filter(Conversation.user_id == user_id).all()]
    q = (
        db.query(Message)
        .filter(Message.conversation_id.in_(conv_ids), Message.role == "user")
        .order_by(Message.created_at.asc())
    )
    attempts = 0
    for m in q:
        low = m.content.lower()
        if any(marker in low for marker in FRUSTRATION_MARKERS):
            attempts += 1
    # emphasize current thread
    cur = (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id, Message.role == "user")
        .order_by(Message.created_at.asc())
        .all()
    )
    thread_attempts = sum(1 for m in cur if any(marker in m.content.lower() for marker in FRUSTRATION_MARKERS))
    return max(attempts, thread_attempts)


def sentiment_trajectory(db: Session, conversation_id: int, last_n: int = 12) -> List[Dict[str, Any]]:
    rows = (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id, Message.role == "user")
        .order_by(Message.created_at.desc())
        .limit(last_n)
        .all()
    )
    rows = list(reversed(rows))
    out = []
    for m in rows:
        label = m.sentiment or "unknown"
        out.append(
            {
                "at": m.created_at.isoformat() if m.created_at else None,
                "sentiment": label,
                "score": m.sentiment_score,
                "preview": (m.content[:120] + "…") if len(m.content) > 120 else m.content,
            }
        )
    return out


def efficacy_summary(db: Session, user_id: int) -> Dict[str, Any]:
    conv_ids = [c.id for c in db.query(Conversation).filter(Conversation.user_id == user_id).all()]
    assistants = (
        db.query(Message)
        .filter(Message.conversation_id.in_(conv_ids), Message.role == "assistant")
        .all()
    )
    rated = [m for m in assistants if m.efficacy_score is not None]
    if not rated:
        return {"sample_size": 0, "positive_rate": None, "note": "No explicit efficacy ratings yet."}
    positives = sum(1 for m in rated if m.efficacy_score >= 0.5)
    return {
        "sample_size": len(rated),
        "positive_rate": round(positives / len(rated), 3),
        "last_rating": rated[-1].efficacy_score if rated else None,
    }


def build_memory_context(
    db: Session,
    user_id: int,
    conversation_id: int,
    recent_sql_messages: List[Message],
    rag_hits: List[Dict[str, Any]],
) -> Dict[str, Any]:
    traj = sentiment_trajectory(db, conversation_id)
    attempts = count_frustration_attempts(db, user_id, conversation_id)
    eff = efficacy_summary(db, user_id)

    channels = Counter()
    for m in recent_sql_messages:
        if m.channel:
            channels[m.channel] += 1
    for h in rag_hits:
        ch = h.get("channel")
        if ch:
            channels[ch] += 1

    escalation_hint = None
    if attempts >= 3:
        escalation_hint = (
            f"This appears to be at least the {attempts}th high-frustration signal across your history. "
            "Acknowledge it, apologize briefly, and offer a senior human handoff or priority path."
        )
    elif attempts == 2:
        escalation_hint = "User may be on a second lap—be extra concrete and avoid repeating generic steps."

    return {
        "sentiment_trajectory": traj,
        "frustration_signals": attempts,
        "efficacy": eff,
        "channels_seen": dict(channels),
        "escalation_hint": escalation_hint,
    }
