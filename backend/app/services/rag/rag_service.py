from langchain_ollama import OllamaLLM

from app.services.rag.index_service import (
    index_upload_directory,
)
from app.services.rag.retrieval_service import (
    search_documents,
)


LLM_MODEL = "qwen2.5:3b"


llm = OllamaLLM(
    model=LLM_MODEL,
    num_predict=512,
    temperature=0,
)


_INDEX_READY = False


def _ensure_index() -> None:

    global _INDEX_READY

    if _INDEX_READY:
        return

    print(
        "RAG: Checking document index..."
    )

    results = index_upload_directory(
        "uploads"
    )

    indexed = sum(
        1
        for result in results
        if result["status"]
        == "indexed"
    )

    existing = sum(
        1
        for result in results
        if result["status"]
        == "already_indexed"
    )

    print(
        f"RAG: indexed={indexed}, "
        f"already_indexed={existing}"
    )

    _INDEX_READY = True


def _build_context(
    documents,
) -> str:

    parts = []

    for index, document in enumerate(
        documents,
        start=1,
    ):

        metadata = (
            document.metadata
            or {}
        )

        source = metadata.get(
            "source",
            "unknown",
        )

        page = metadata.get(
            "page",
            "unknown",
        )

        chunk = metadata.get(
            "chunk_index",
            0,
        )

        parts.append(
            f"[DOCUMENT {index}]\n"
            f"FILE: {source}\n"
            f"PAGE: {page}\n"
            f"CHUNK: {chunk}\n"
            f"CONTENT:\n"
            f"{document.page_content}"
        )

    return "\n\n".join(parts)


def ask_rag(
    question: str,
) -> str:

    _ensure_index()

    documents = search_documents(
        question
    )

    print(
        "SELECTED DOCUMENTS:",
        len(documents),
    )

    if not documents:

        return (
            "The requested information is not available "
            "in the provided documents."
        )

    context = _build_context(
        documents
    )

    prompt = f"""
You are a precise document question-answering assistant.

Use ONLY the DOCUMENT CONTEXT.

USER QUESTION:
{question}

DOCUMENT CONTEXT:
{context}

RULES:

1. Answer only from the supplied documents.

2. Carefully inspect every supplied document section.

3. Preserve names, numbers, dates, course codes,
   titles and times exactly as written.

4. If the user asks for ALL items, return ALL matching
   items present in the supplied context.

5. Do not stop after finding the first matching item.

6. If the question asks for practical/lab examinations,
   include practical/lab examinations only.

7. If the question asks for written examinations,
   include written examinations only.

8. Do not mix written and practical examinations.

9. Do not mix information belonging to unrelated files.

10. Do not invent missing information.

11. Do not guess.

12. If the requested information is genuinely absent,
    say:

The requested information is not available in the provided documents.

13. Give a direct answer.

14. For multiple results use a numbered or bullet list.

15. Do not mention retrieval, embeddings, Chroma,
    vector databases, chunks, semantic search or
    internal system details.

ANSWER:
"""

    response = llm.invoke(
        prompt
    )

    return response.strip()