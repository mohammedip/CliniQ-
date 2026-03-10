from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db
import httpx
import os

router = APIRouter(prefix="/health", tags=["health"])

OLLAMA_URL = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")


@router.get("/")
async def health_check(db: Session = Depends(get_db)):
    status = {
        "status": "healthy",
        "services": {
            "api": "ok",
            "database": "ok",
            "ollama": "ok",
        }
    }

    # Check database
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        status["services"]["database"] = f"error: {str(e)}"
        status["status"] = "degraded"

    # Check Ollama
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            res = await client.get(f"{OLLAMA_URL}/api/tags")
            if res.status_code != 200:
                raise Exception(f"status {res.status_code}")
    except Exception as e:
        status["services"]["ollama"] = f"error: {str(e)}"
        status["status"] = "degraded"

    return status