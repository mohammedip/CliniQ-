import os
import time
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama import OllamaLLM
from .load_chunck_pdf import load_split_get_vectorstore
from .query_expansion import retrieve_with_expansion
from .reranking import rerank_docs
from app.services.mlflow_service import log_rag_query
from app.services.deepeval_service import evaluate_rag
from app.core.metrics import record_rag_query
import concurrent.futures
import threading

pdf_path = os.getenv("PDF_PATH", "/core/docs/manual.md")
CHROMA_DIR = os.getenv("CHROMA_DIR", "/core/chroma_db")
OLLAMA_URL = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")


def get_llm():
    model_name = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
    return OllamaLLM(
        model=model_name,
        base_url=OLLAMA_URL,
        temperature=0.0,
        num_predict=4096,
        top_p=0.9,
        top_k=40,
    )


def get_fast_llm():
    model_name = os.getenv("OLLAMA_FAST_MODEL", "llama3.2:3b")
    return OllamaLLM(
        model=model_name,
        base_url=OLLAMA_URL,
        temperature=0.0,
        num_predict=1024,
        top_p=0.9,
        top_k=40,
    )


def create_retriever(vectorstore):
    return vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 20}
    )


def format_docs(docs):
    return "\n\n".join(
        f"--- chunk {i+1} ---\n{d.page_content}"
        for i, d in enumerate(docs)
    )


def get_rag_prompt():
    return ChatPromptTemplate.from_template("""
You are a medical assistant answering questions based ONLY on the context below.
Always answer in the same language as the question.
Be precise and concise.

Context:
{context}

Question:
{question}

If the answer is not in the context, say in the same language as the question:
"I don't know based on the provided document."

Answer:
""")

_vectorstore = None

def get_vectorstore():
    global _vectorstore
    if _vectorstore is None:
        _vectorstore = load_split_get_vectorstore(pdf_path, CHROMA_DIR)
    return _vectorstore


def build_self_rag_chain(user_id: int = None):
    vectorstore = get_vectorstore()
    retriever = create_retriever(vectorstore)
    llm = get_llm()
    fast_llm = get_fast_llm()
    rag_prompt = get_rag_prompt()

    def self_rag_logic(question: str) -> str:
        start_time = time.time()

        try:
            # Step 1: Query expansion + retrieval
            docs = retrieve_with_expansion(question, retriever, fast_llm)

            print(f"=== RETRIEVED {len(docs)} DOCS ===")
            for i, doc in enumerate(docs):
                print(f"--- doc {i+1} ---\n{doc.page_content[:200]}\n")

            # Step 2: Rerank
            reranked_docs = rerank_docs(question, docs, fast_llm, top_k=5)

            print(f"=== RERANKED {len(reranked_docs)} DOCS ===")
            for i, doc in enumerate(reranked_docs):
                print(f"--- reranked {i+1} ---\n{doc.page_content[:200]}\n")

            context = format_docs(reranked_docs)
            contexts_list = [doc.page_content for doc in reranked_docs]

            # Step 3: Generate answer
            answer = (rag_prompt | llm | StrOutputParser()).invoke({
                "context": context,
                "question": question
            })

            print(f"=== ANSWER ===\n{answer}\n")

            latency = time.time() - start_time

            # Step 4: Record Prometheus metrics
            record_rag_query(latency=latency, grounded=True)

            # Step 5 & 6: DeepEval + MLflow in background (don't block the response)
            def run_background(q, ans, ctx_list, ctx, lat, uid):
                try:
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(evaluate_rag, q, ans, ctx_list)
                        metrics = future.result(timeout=180)
                except Exception as e:
                    print(f"⚠️ DeepEval failed: {e}")
                    metrics = {}
                try:
                    log_rag_query(
                        question=q,
                        context=ctx,
                        answer=ans,
                        grade="NO_GRADER",
                        latency_seconds=lat,
                        user_id=uid,
                        metrics=metrics,
                    )
                except Exception as e:
                    print(f"⚠️ MLflow logging failed: {e}")

            
            thread = threading.Thread(
                target=run_background,
                args=(question, answer, contexts_list, context, latency, user_id)
            )
            thread.daemon = True
            thread.start()


            return answer

        except Exception as e:
            latency = time.time() - start_time
            record_rag_query(latency=latency, grounded=False, failed=True)
            raise e

    return RunnableLambda(self_rag_logic)