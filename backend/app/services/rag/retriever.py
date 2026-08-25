from app.services.rag.vector_store import get_vector_store


def retrieve_context(query: str, k: int = 4) -> str:
    """
    Search the vector database and return the most relevant chunks.
    """

    db = get_vector_store()

    docs = db.similarity_search(query, k=k)

    if not docs:
        return ""

    context = "\n\n".join(doc.page_content for doc in docs)

    return context