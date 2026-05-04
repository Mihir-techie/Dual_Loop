from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.db import get_db
from database.models import Conversation, Message, User
from deps import get_current_user
from schemas.schemas import ChatRequest
from services.llm_service import generate_support_reply
from services.memory_analytics import (
    build_memory_context,
    detect_sentiment_detailed,
    sentiment_trajectory,
    thread_frustration_signals,
)
from services.qdrant_service import search_similar, upsert_memory_point

router = APIRouter(tags=["chat"])


@router.post("/conversations/{conversation_id}/chat")
def chat_in_conversation(
    conversation_id: int,
    body: ChatRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    conv = db.query(Conversation).filter(Conversation.id == conversation_id, Conversation.user_id == user.id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    channel = body.channel or conv.channel or "chat"
    user_label, user_score = detect_sentiment_detailed(body.message)

    user_msg = Message(
        conversation_id=conv.id,
        role="user",
        content=body.message,
        sentiment=user_label,
        sentiment_score=user_score,
        channel=channel,
    )
    db.add(user_msg)
    conv.updated_at = datetime.utcnow()
    # Flush so the thread query includes this turn, but do NOT commit until the
    # model succeeds — otherwise a failed LLM call leaves a "stuck" user-only message.
    db.flush()
    db.refresh(user_msg)

    try:
        thread = (
            db.query(Message)
            .filter(Message.conversation_id == conv.id)
            .order_by(Message.created_at.asc())
            .all()
        )

        rag_hits: list = []
        if user.memory_consent and not body.compare_without_memory:
            try:
                rag_hits = search_similar(user.id, body.message, limit=6)
            except Exception:
                rag_hits = []

        analytics = build_memory_context(db, user.id, conv.id, thread, rag_hits)
        if not user.memory_consent:
            tf = thread_frustration_signals(thread)
            esc = None
            if tf >= 3:
                esc = "Multiple frustration signals in this thread — acknowledge and offer escalation."
            elif tf == 2:
                esc = "Second lap in-thread — be concrete and avoid generic scripts."
            analytics = {
                "sentiment_trajectory": sentiment_trajectory(db, conv.id),
                "frustration_signals": tf,
                "efficacy": {"note": "Cross-session efficacy suppressed without long-term memory consent."},
                "channels_seen": {},
                "escalation_hint": esc,
            }

        baseline_reply = None
        if body.compare_without_memory:
            baseline_reply = generate_support_reply(
                body.message,
                rag_hits=[],
                sql_messages=[],
                analytics={"note": "baseline mode — no memory"},
                memory_disabled=True,
                user_display_name=user.display_name,
                consent=user.memory_consent,
            )

        reply = generate_support_reply(
            body.message,
            rag_hits=rag_hits if user.memory_consent else [],
            sql_messages=thread,
            analytics=analytics,
            memory_disabled=False,
            user_display_name=user.display_name,
            consent=user.memory_consent,
        )
        if not reply or not str(reply).strip():
            raise RuntimeError("Model returned an empty reply.")

        asst = Message(
            conversation_id=conv.id,
            role="assistant",
            content=str(reply).strip(),
            sentiment=None,
            sentiment_score=None,
            channel=channel,
        )
        db.add(asst)
        conv.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(asst)
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=503,
            detail=(
                "The assistant could not complete this turn (often: missing/invalid GROQ_API_KEY, "
                "model error, or network). "
                f"Technical detail: {str(e)[:400]}"
            ),
        ) from e

    if user.memory_consent:
        doc = f"USER ({channel}): {body.message}\nASSISTANT: {reply}"
        try:
            upsert_memory_point(
                user.id,
                conv.id,
                asst.id,
                document=doc,
                payload={
                    "channel": channel,
                    "sentiment": user_label,
                    "created_at": datetime.utcnow().isoformat(),
                },
            )
        except Exception:
            pass

    evolution_note = None
    prior_assistant = [m for m in thread if m.role == "assistant"]
    if len(prior_assistant) >= 1:
        evolution_note = (
            f"This is assistant turn #{len(prior_assistant) + 1} in this thread — deepen the diagnosis, "
            "reference what already failed, and tighten next steps."
        )

    return {
        "reply": reply,
        "baseline_reply": baseline_reply,
        "comparison_mode": body.compare_without_memory,
        "message_id": asst.id,
        "user_message_id": user_msg.id,
        "rag_hits": rag_hits,
        "analytics": analytics,
        "sentiment": {"label": user_label, "score": user_score},
        "evolution_note": evolution_note,
        "privacy": {
            "memory_consent": user.memory_consent,
            "stored_in": ["sqlite_transcript", "qdrant_semantic"] if user.memory_consent else ["sqlite_transcript"],
        },
    }
