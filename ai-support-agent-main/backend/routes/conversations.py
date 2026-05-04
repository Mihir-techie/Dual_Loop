from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.db import get_db
from database.models import Conversation, Message, User
from deps import get_current_user
from schemas.schemas import ChatRequest, ConversationCreate, ConversationOut, EfficacyFeedback

router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.get("", response_model=List[ConversationOut])
def list_conversations(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    rows = (
        db.query(Conversation)
        .filter(Conversation.user_id == user.id)
        .order_by(Conversation.updated_at.desc())
        .all()
    )
    return rows


@router.post("", response_model=ConversationOut)
def create_conversation(
    body: ConversationCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    conv = Conversation(
        user_id=user.id,
        title=body.title or "New chat",
        channel=body.channel or "chat",
    )
    db.add(conv)
    db.commit()
    db.refresh(conv)
    return conv


@router.get("/{conversation_id}/messages")
def get_messages(
    conversation_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    conv = db.query(Conversation).filter(Conversation.id == conversation_id, Conversation.user_id == user.id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    msgs = (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
        .all()
    )
    return [
        {
            "id": m.id,
            "role": m.role,
            "content": m.content,
            "sentiment": m.sentiment,
            "sentiment_score": m.sentiment_score,
            "channel": m.channel,
            "created_at": m.created_at.isoformat() if m.created_at else None,
        }
        for m in msgs
    ]


@router.post("/{conversation_id}/feedback")
def post_efficacy(
    conversation_id: int,
    body: EfficacyFeedback,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    conv = db.query(Conversation).filter(Conversation.id == conversation_id, Conversation.user_id == user.id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    msg = (
        db.query(Message)
        .filter(
            Message.id == body.message_id,
            Message.conversation_id == conversation_id,
            Message.role == "assistant",
        )
        .first()
    )
    if not msg:
        raise HTTPException(status_code=404, detail="Assistant message not found")
    msg.efficacy_score = 1.0 if body.helpful else 0.0
    db.commit()
    return {"ok": True, "message_id": msg.id, "efficacy_score": msg.efficacy_score}
