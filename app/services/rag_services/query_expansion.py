from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


def get_query_expansion_prompt():
    return ChatPromptTemplate.from_template("""
You are an expert at reformulating medical questions to improve document retrieval.

Given the original question below, generate 3 different versions of it.
IMPORTANT: Keep ALL questions in the exact same language as the original.
Do not translate. Do not switch languages.
Each version should approach the question from a slightly different angle.
                                            
Original question: {question}

Output ONLY the 3 questions, one per line, no numbering, no explanation.
""")


def expand_query(question: str, llm) -> list[str]:
    prompt = get_query_expansion_prompt()
    chain = prompt | llm | StrOutputParser()
    result = chain.invoke({"question": question})
    expanded = [q.strip() for q in result.strip().split("\n") if q.strip()]
    # Always include the original question
    return [question] + expanded[:3]


def retrieve_with_expansion(question: str, retriever, llm) -> list:
    queries = expand_query(question, llm)
    seen_contents = set()
    all_docs = []

    for query in queries:
        docs = retriever.invoke(query)
        for doc in docs:
            content_key = doc.page_content[:100]
            if content_key not in seen_contents:
                seen_contents.add(content_key)
                all_docs.append(doc)

    return all_docs