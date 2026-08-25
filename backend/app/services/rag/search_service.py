from app.services.rag.vector_store import get_vector_store


def search_documents(query: str, k: int = 8):
    """
    Search the Chroma vector database for relevant
    document chunks and print similarity scores.
    """

    db = get_vector_store()

    results = db.similarity_search_with_score(
        query,
        k=k,
    )

    docs = []

    print("\n==========================")
    print("QUERY:")
    print(query)
    print("==========================")

    print(f"Retrieved {len(results)} chunks")

    for i, (doc, score) in enumerate(results):

        print(f"\n------ CHUNK {i + 1} ------")
        print(f"Score: {score}")
        print(doc.page_content[:800])

        docs.append(doc)

    print("==========================\n")

    return docs