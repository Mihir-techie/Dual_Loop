from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database.db import Base, engine
from database import models  # noqa: F401 — register models
from routes import auth, chat, conversations, demo, memory_stats
from services.qdrant_service import get_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    try:
        get_client()
    except Exception:
        pass
    yield


app = FastAPI(title="Cognitive Support Agent", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(conversations.router)
app.include_router(chat.router)
app.include_router(memory_stats.router)
app.include_router(demo.router)


@app.get("/")
def home():
    return {
        "message": "Cognitive Support Agent API",
        "docs": "/docs",
        "memory": "Memory-first: SQLite transcript + Qdrant semantic RAG",
    }
