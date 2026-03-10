from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):

    # ─── Database ──────────────────────────────────────────────────────────────
    DATABASE_URL: str = "postgresql://cliniq:cliniq@postgres:5432/cliniq"

    # ─── JWT Auth ──────────────────────────────────────────────────────────────
    SECRET_KEY: str = "secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ─── Ollama ────────────────────────────────────────────────────────────────
    OLLAMA_BASE_URL: str = "http://ollama:11434"
    OLLAMA_MODEL: str = "llama3.1:8b"
    OLLAMA_FAST_MODEL: str = "llama3.2:3b"

    # ─── RAG ───────────────────────────────────────────────────────────────────
    CHROMA_DIR: str = "/core/chroma_db"
    PDF_PATH: str = "/core/docs/manual.md"
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 100
    RETRIEVAL_K: int = 10
    RERANKING_TOP_K: int = 5
    EMBEDDING_MODEL: str = "intfloat/multilingual-e5-base"

    # ─── MLflow ────────────────────────────────────────────────────────────────
    MLFLOW_TRACKING_URI: str = "http://mlflow:5000"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()