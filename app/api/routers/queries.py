from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.query import RAGRequest, QueryResponse
from app.services.rag_services.rag import build_self_rag_chain
from app.services.query_services import save_query, get_user_queries, get_all_queries
from app.core.dependencies import get_current_user, require_admin
from app.models.user import User

router = APIRouter(prefix="/queries", tags=["queries"])




# ─── Ask a question ────────────────────────────────────────────────────────────
@router.post("/ask", response_model=dict)
async def ask_question(
    request: RAGRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        rag_chain = build_self_rag_chain(user_id=current_user.id)
        rag_result = rag_chain.invoke(request.question)

        save_query(
            db=db,
            user_id=current_user.id,
            question=request.question,
            answer=rag_result,
        )

        return {"answer": rag_result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RAG query failed: {str(e)}")


# ─── Get current user history ──────────────────────────────────────────────────
@router.get("/history", response_model=list[QueryResponse])
def get_history(
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_user_queries(db, user_id=current_user.id, limit=limit)


# ─── Admin: get all queries ────────────────────────────────────────────────────
@router.get("/history/all", response_model=list[QueryResponse])
def get_all_history(
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    return get_all_queries(db, limit=limit)