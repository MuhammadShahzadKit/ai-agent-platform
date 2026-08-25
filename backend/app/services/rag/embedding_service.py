from functools import lru_cache

from langchain_ollama import OllamaEmbeddings


EMBEDDING_MODEL = "nomic-embed-text"


@lru_cache(maxsize=1)
def get_embeddings() -> OllamaEmbeddings:
    """
    Return one shared embedding model instance.

    Cached so the model object is created only once
    during the application lifetime.
    """

    return OllamaEmbeddings(
        model=EMBEDDING_MODEL,
    )