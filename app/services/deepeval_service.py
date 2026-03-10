from deepeval.models.base_model import DeepEvalBaseLLM
from deepeval.metrics import (
    AnswerRelevancyMetric,
    FaithfulnessMetric,
    ContextualPrecisionMetric,
    ContextualRecallMetric,
)
from deepeval.test_case import LLMTestCase
from langchain_ollama import OllamaLLM
from typing import Optional
import os
import asyncio
import concurrent.futures


OLLAMA_URL = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")


# ─── Custom Ollama Judge Model for DeepEval ────────────────────────────────────

class OllamaJudge(DeepEvalBaseLLM):

    def __init__(self):
        self.llm = OllamaLLM(
            model=OLLAMA_MODEL,
            base_url=OLLAMA_URL,
            temperature=0.0,
        )

    def load_model(self):
        return self.llm

    def generate(self, prompt: str) -> str:
        enhanced_prompt = f"""You are a JSON-only response system.
        {prompt}

        CRITICAL RULES:
        - Respond with ONLY a valid JSON object
        - No markdown, no backticks, no explanation
        - No text before or after the JSON
        - Start your response with {{ and end with }}"""
        return self.llm.invoke(enhanced_prompt)

    async def a_generate(self, prompt: str) -> str:
        loop = asyncio.get_event_loop()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            return await loop.run_in_executor(executor, self.generate, prompt)

    def get_model_name(self) -> str:
        return OLLAMA_MODEL


# ─── RAG Evaluation ────────────────────────────────────────────────────────────

def evaluate_rag(
    question: str,
    answer: str,
    contexts: list[str],
    ground_truth: Optional[str] = None,
) -> dict:

    try:
        model = OllamaJudge()

        test_case = LLMTestCase(
            input=question,
            actual_output=answer,
            retrieval_context=contexts,
            expected_output=ground_truth or answer,
        )

        results = {}

        try:
            metric = AnswerRelevancyMetric(threshold=0.5, model=model)
            metric.measure(test_case)
            results["answer_relevance"] = metric.score
        except Exception as e:
            print(f"⚠️ Answer relevance eval failed: {e}")
            results["answer_relevance"] = 0.0

        try:
            metric = FaithfulnessMetric(threshold=0.5, model=model)
            metric.measure(test_case)
            results["faithfulness"] = metric.score
        except Exception as e:
            print(f"⚠️ Faithfulness eval failed: {e}")
            results["faithfulness"] = 0.0

        try:
            metric = ContextualPrecisionMetric(threshold=0.5, model=model)
            metric.measure(test_case)
            results["precision_at_k"] = metric.score
        except Exception as e:
            print(f"⚠️ Precision@k eval failed: {e}")
            results["precision_at_k"] = 0.0

        try:
            metric = ContextualRecallMetric(threshold=0.5, model=model)
            metric.measure(test_case)
            results["recall_at_k"] = metric.score
        except Exception as e:
            print(f"⚠️ Recall@k eval failed: {e}")
            results["recall_at_k"] = 0.0

        print(f"📊 RAG Evaluation: {results}")
        return results

    except Exception as e:
        print(f"⚠️ DeepEval failed: {e}")
        return {
            "answer_relevance": 0.0,
            "faithfulness": 0.0,
            "precision_at_k": 0.0,
            "recall_at_k": 0.0,
        }