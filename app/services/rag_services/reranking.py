from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


def get_reranker_prompt():
    return ChatPromptTemplate.from_template("""
You are a relevance judge. Given a question and a document chunk,
score how relevant the chunk is to answering the question.

Question: {question}

Document chunk:
{chunk}

Respond ONLY with a single integer from 0 to 10. Nothing else.
""")


def rerank_docs(question: str, docs: list, llm, top_k: int = 5) -> list:
    reranker_prompt = get_reranker_prompt()
    scored_docs = []

    for doc in docs:
        try:
            score_str = (reranker_prompt | llm | StrOutputParser()).invoke({
                "question": question,
                "chunk": doc.page_content[:500]
            })
            score = float(''.join(filter(lambda c: c.isdigit() or c == '.', score_str.strip()[:5])))
        except Exception:
            score = 0.0
            
        print(f"SCORE {score} | {doc.page_content[:80]}")

        scored_docs.append((score, doc))

    scored_docs.sort(key=lambda x: x[0], reverse=True)
    return [doc for _, doc in scored_docs[:top_k]]