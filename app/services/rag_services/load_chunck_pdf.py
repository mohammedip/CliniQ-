from langchain_chroma import Chroma
from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from app.core.config import get_settings
import os

settings = get_settings()


class E5Embeddings(HuggingFaceEmbeddings):
    def embed_query(self, text: str):

        return super().embed_query("query: " + text)

    def embed_documents(self, texts):

        texts = ["passage: " + t for t in texts]
        return super().embed_documents(texts)


def load_split_get_vectorstore(path: str = None, chroma_dir: str = None):

    pdf = path or settings.PDF_PATH
    chroma = chroma_dir or settings.CHROMA_DIR

    embeddings = E5Embeddings(
        model_name=settings.EMBEDDING_MODEL
    )

    if os.path.exists(chroma) and os.listdir(chroma):
        vectorstore = Chroma(
            persist_directory=chroma,
            embedding_function=embeddings,
        )

    else:

        loader = UnstructuredMarkdownLoader(pdf)
        documents = loader.load()


        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            separators=["\n\n", "\n", ". ", " ", ""],
        )

        chunks = text_splitter.split_documents(documents)

        if chunks:
            print("First chunk preview:")
            print(chunks[0].page_content[:300])


        vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            persist_directory=chroma,
        )

    return vectorstore