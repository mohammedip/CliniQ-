import pytest
from unittest.mock import MagicMock, patch
from app.services.rag_services.query_expansion import expand_query, retrieve_with_expansion
from app.services.rag_services.reranking import rerank_docs


# ─── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def mock_llm():
    llm = MagicMock()
    return llm


@pytest.fixture
def mock_retriever():
    retriever = MagicMock()
    return retriever


@pytest.fixture
def mock_docs():
    doc1 = MagicMock()
    doc1.page_content = "La toux est souvent causée par une infection virale."
    doc1.metadata = {"page": 1}

    doc2 = MagicMock()
    doc2.page_content = "Le traitement de la toux inclut du repos et de l'hydratation."
    doc2.metadata = {"page": 2}

    doc3 = MagicMock()
    doc3.page_content = "Une toux persistante peut indiquer une pneumonie ou tuberculose."
    doc3.metadata = {"page": 3}

    return [doc1, doc2, doc3]


# ─── Query Expansion Tests ─────────────────────────────────────────────────────

class TestQueryExpansion:

    def test_expand_query_returns_list(self, mock_llm):
        with patch("app.services.rag_services.query_expansion.ChatPromptTemplate") as mock_prompt, \
             patch("app.services.rag_services.query_expansion.StrOutputParser"):

            mock_chain = MagicMock()
            mock_chain.invoke.return_value = "question 1\nquestion 2\nquestion 3"
            mock_prompt.from_template.return_value.__or__ = MagicMock(return_value=mock_chain)

            result = expand_query("causes de la toux", mock_llm)

        assert isinstance(result, list)
        # Always includes original question
        assert "causes de la toux" in result

    def test_expand_query_includes_original(self, mock_llm):
        with patch("app.services.rag_services.query_expansion.ChatPromptTemplate") as mock_prompt, \
             patch("app.services.rag_services.query_expansion.StrOutputParser"):

            mock_chain = MagicMock()
            mock_chain.invoke.return_value = "q1\nq2\nq3"
            mock_prompt.from_template.return_value.__or__ = MagicMock(return_value=mock_chain)

            original = "c est quoi la diarrhée"
            result = expand_query(original, mock_llm)

        assert result[0] == original

    def test_retrieve_with_expansion_deduplicates(self, mock_retriever, mock_llm, mock_docs):
        # Return same docs for all queries to test deduplication
        mock_retriever.invoke.return_value = mock_docs

        with patch("app.services.rag_services.query_expansion.expand_query",
                   return_value=["question 1", "question 2", "question 3"]):
            result = retrieve_with_expansion("toux", mock_retriever, mock_llm)

        # Should deduplicate — same docs returned 3 times should still be 3 unique docs
        assert len(result) == len(mock_docs)

    def test_retrieve_with_expansion_calls_retriever(self, mock_retriever, mock_llm, mock_docs):
        mock_retriever.invoke.return_value = mock_docs

        with patch("app.services.rag_services.query_expansion.expand_query",
                   return_value=["q1", "q2"]):
            retrieve_with_expansion("toux", mock_retriever, mock_llm)

        # Retriever should be called once per expanded query
        assert mock_retriever.invoke.call_count == 2


# ─── Reranking Tests ───────────────────────────────────────────────────────────

class TestReranking:

    def test_rerank_returns_top_k(self, mock_llm, mock_docs):
        with patch("app.services.rag_services.reranking.ChatPromptTemplate") as mock_prompt, \
             patch("app.services.rag_services.reranking.StrOutputParser"):

            mock_chain = MagicMock()
            mock_chain.invoke.side_effect = ["8", "5", "9"]
            mock_prompt.from_template.return_value.__or__ = MagicMock(return_value=mock_chain)

            result = rerank_docs("toux", mock_docs, mock_llm, top_k=2)

        assert len(result) == 2

    def test_rerank_sorts_by_score(self, mock_llm, mock_docs):
        with patch("app.services.rag_services.reranking.ChatPromptTemplate") as mock_prompt, \
             patch("app.services.rag_services.reranking.StrOutputParser"):

            mock_chain = MagicMock()
            # doc1=3, doc2=9, doc3=6 → sorted: doc2, doc3, doc1
            mock_chain.invoke.side_effect = ["3", "9", "6"]
            mock_prompt.from_template.return_value.__or__ = MagicMock(return_value=mock_chain)

            result = rerank_docs("toux", mock_docs, mock_llm, top_k=3)

        # doc2 should be first (score 9)
        assert result[0].page_content == mock_docs[1].page_content

    def test_rerank_handles_invalid_score(self, mock_llm, mock_docs):
        with patch("app.services.rag_services.reranking.ChatPromptTemplate") as mock_prompt, \
             patch("app.services.rag_services.reranking.StrOutputParser"):

            mock_chain = MagicMock()
            # Invalid score responses — should default to 0
            mock_chain.invoke.side_effect = ["not a number", "YES", "???"]
            mock_prompt.from_template.return_value.__or__ = MagicMock(return_value=mock_chain)

            # Should not raise an exception
            result = rerank_docs("toux", mock_docs, mock_llm, top_k=3)

        assert isinstance(result, list)

    def test_rerank_top_k_larger_than_docs(self, mock_llm, mock_docs):
        with patch("app.services.rag_services.reranking.ChatPromptTemplate") as mock_prompt, \
             patch("app.services.rag_services.reranking.StrOutputParser"):

            mock_chain = MagicMock()
            mock_chain.invoke.side_effect = ["5", "7", "3"]
            mock_prompt.from_template.return_value.__or__ = MagicMock(return_value=mock_chain)

            # top_k=10 but only 3 docs
            result = rerank_docs("toux", mock_docs, mock_llm, top_k=10)

        assert len(result) == len(mock_docs)