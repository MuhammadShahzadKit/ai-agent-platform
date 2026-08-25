from pathlib import Path
from functools import lru_cache

from langchain_chroma import Chroma

from app.services.rag.embedding_service import get_embeddings


BASE_DIR = Path(__file__).resolve().parents[4]

DB_PATH = BASE_DIR / "storage" / "chroma_db"

DB_PATH.mkdir(
    parents=True,
    exist_ok=True,
)


COLLECTION_NAME = "ai_agent_documents"


@lru_cache(maxsize=1)
def get_vector_store() -> Chroma:
    """
    Return the single persistent Chroma collection.

    Chroma is initialized once and reused for the lifetime
    of the Python process.
    """

    return Chroma(
        collection_name=COLLECTION_NAME,
        persist_directory=str(DB_PATH),
        embedding_function=get_embeddings(),
    )