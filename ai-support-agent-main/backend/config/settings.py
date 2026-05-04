import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

_BACKEND_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(_BACKEND_ROOT / ".env")

_DEFAULT_QDRANT = _BACKEND_ROOT / "data" / "qdrant"


class Settings(BaseSettings):
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")
    jwt_secret: str = os.getenv("JWT_SECRET", "change-me-in-production-use-openssl-rand")
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7

    qdrant_path: str = os.getenv("QDRANT_PATH", str(_DEFAULT_QDRANT))
    collection_name: str = "support_memory"
    rag_top_k: int = 6

    llm_model: str = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

    class Config:
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
