from langchain_community.vectorstores.pgvector import PGVector
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document
import os
from dotenv import load_dotenv
import sys

load_dotenv()

CONNECTION_STRING = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://user:pass@localhost:5432/sopdb"
)
COLLECTION_NAME = "sop_documents"
TOP_K = int(os.getenv("TOP_K", 6))

_embeddings = None
_embeddings_init_attempted = False


def _get_embeddings():
    global _embeddings, _embeddings_init_attempted

    if _embeddings is not None:
        return _embeddings

    if _embeddings_init_attempted:
        return None

    _embeddings_init_attempted = True
    try:
        # Lazy-init so container startup is not blocked by model download.
        _embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        return _embeddings
    except Exception as exc:  # ImportError or version mismatch from HF hub
        print("WARNING: HuggingFace embeddings unavailable:", exc, file=sys.stderr)
        return None


def get_vectorstore() -> PGVector:
    embeddings = _get_embeddings()
    if embeddings is None:
        raise RuntimeError("Embeddings backend not available")
    return PGVector(
        collection_name=COLLECTION_NAME,
        connection_string=CONNECTION_STRING,
        embedding_function=embeddings,
    )


def store(docs: list[Document]) -> int:
    embeddings = _get_embeddings()
    if embeddings is None:
        print("Skipping storing documents: embeddings unavailable", file=sys.stderr)
        return 0
    PGVector.from_documents(
        docs,
        embeddings,
        collection_name=COLLECTION_NAME,
        connection_string=CONNECTION_STRING,
        pre_delete_collection=False,
    )
    return len(docs)


def search(query: str, k: int = TOP_K) -> list[Document]:
    """Semantic search — query → embedding → cosine similarity → top-k chunks."""
    return get_vectorstore().similarity_search(query, k=k)


def search_with_score(query: str, k: int = TOP_K) -> list[tuple[Document, float]]:
    """Same as search but returns (doc, cosine_distance) tuples."""
    return get_vectorstore().similarity_search_with_score(query, k=k)
