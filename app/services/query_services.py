from sqlalchemy.orm import Session
from app.models.query import Query


def get_user_queries(db: Session, user_id: int, limit: int = 50) -> list[Query]:
    return (
        db.query(Query)
        .filter(Query.user_id == user_id)
        .order_by(Query.created_at.desc())
        .limit(limit)
        .all()
    )


def get_all_queries(db: Session, limit: int = 100) -> list[Query]:
    return (
        db.query(Query)
        .order_by(Query.created_at.desc())
        .limit(limit)
        .all()
    )


def save_query(db: Session, user_id: int, question: str, answer: str) -> Query:
    query = Query(
        user_id=user_id,
        query=question,
        response=answer,
    )
    db.add(query)
    db.commit()
    db.refresh(query)
    return query