import mlflow
import os
from typing import Optional

MLFLOW_URI = os.getenv("MLFLOW_TRACKING_URI", "http://mlflow:5000")
EXPERIMENT_NAME = "protocare_rag"


def init_mlflow():
    try:
        mlflow.set_tracking_uri(MLFLOW_URI)
        mlflow.set_experiment(EXPERIMENT_NAME)
        print("✅ MLflow connected")
    except Exception as e:
        print(f"⚠️ MLflow init failed (non-critical): {e}")


def log_rag_config():
    try:
        with mlflow.start_run(run_name="rag_config"):
            mlflow.log_params({
                "chunk_size": 500,
                "chunk_overlap": 100,
                "chunking_strategy": "RecursiveCharacterTextSplitter",
                "separators": "[\\n\\n, \\n, '. ', ' ', '']",
            })
            mlflow.log_params({
                "embedding_model": "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
                "embedding_dimensions": 384,
                "embedding_normalization": True,
                "vectorstore": "ChromaDB",
            })
            mlflow.log_params({
                "similarity_algorithm": "cosine",
                "retrieval_k": 10,
                "reranking": True,
                "reranking_top_k": 5,
                "query_expansion": True,
                "query_expansion_n": 3,
            })
            mlflow.log_params({
                "llm_model": os.getenv("OLLAMA_MODEL", "llama3.1:8b"),
                "fast_llm_model": os.getenv("OLLAMA_FAST_MODEL", "llama3.2:3b"),
                "llm_temperature": 0.0,
                "llm_max_tokens": 4096,
            })
        print("✅ RAG config logged to MLflow")
    except Exception as e:
        print(f"⚠️ MLflow config logging failed (non-critical): {e}")


def log_rag_query(
    question: str,
    context: str,
    answer: str,
    grade: str,
    latency_seconds: float,
    user_id: Optional[int] = None,
    metrics: Optional[dict] = None,
):
    try:
        with mlflow.start_run(run_name="rag_query"):
            mlflow.log_param("question", question[:250])
            mlflow.log_param("user_id", user_id)
            mlflow.log_param("grade", grade)
            mlflow.log_metric("latency_seconds", latency_seconds)
            mlflow.log_metric("answer_grounded", 1.0 if "YES" in grade.upper() else 0.0)

            with open("/tmp/rag_context.txt", "w") as f:
                f.write(f"QUESTION:\n{question}\n\nCONTEXT:\n{context}\n\nANSWER:\n{answer}")
            mlflow.log_artifact("/tmp/rag_context.txt")

            if metrics:
                mlflow.log_metrics({
                    "answer_relevance": metrics.get("answer_relevance", 0.0),
                    "faithfulness": metrics.get("faithfulness", 0.0),
                    "precision_at_k": metrics.get("precision_at_k", 0.0),
                    "recall_at_k": metrics.get("recall_at_k", 0.0),
                })
    except Exception as e:
        print(f"⚠️ MLflow query logging failed (non-critical): {e}")