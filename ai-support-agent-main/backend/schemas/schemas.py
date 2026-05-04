from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    display_name: str = Field(min_length=1, max_length=120)
    memory_consent: bool = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ConversationCreate(BaseModel):
    title: Optional[str] = "New chat"
    channel: str = "chat"


class ConversationOut(BaseModel):
    id: int
    title: str
    channel: str

    class Config:
        from_attributes = True


class ChatRequest(BaseModel):
    message: str = Field(min_length=1)
    channel: Optional[str] = "chat"
    compare_without_memory: bool = False


class EfficacyFeedback(BaseModel):
    message_id: int
    helpful: bool
