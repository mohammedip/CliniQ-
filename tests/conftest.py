import pytest
from unittest.mock import MagicMock, patch
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


sys.modules["langchain_ollama"] = MagicMock()
sys.modules["langchain_community"] = MagicMock()
sys.modules["langchain_community.vectorstores"] = MagicMock()
sys.modules["langchain_community.document_loaders"] = MagicMock()
sys.modules["langchain_huggingface"] = MagicMock()
sys.modules["chromadb"] = MagicMock()