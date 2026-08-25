import ollama

from app.services.rag.retrieval_service import search_documents
from app.services.rag.prompt_builder import build_rag_prompt


def _should_use_rag(prompt: str) -> bool:
    """
    Decide whether a user message is likely asking about
    information that may exist in uploaded documents.

    This is intentionally lightweight. It does not call an AI
    model just to decide whether RAG should be used.
    """

    text = (prompt or "").strip().lower()

    if not text:
        return False

    # --------------------------------------------------------
    # Clearly general / conversational messages
    # --------------------------------------------------------

    general_phrases = {
        "hello",
        "hi",
        "hey",
        "hello there",
        "hi there",
        "hey there",
        "good morning",
        "good afternoon",
        "good evening",
        "good night",
        "how are you",
        "how are you?",
        "are you working",
        "are you working?",
        "are you there",
        "are you there?",
        "who are you",
        "who are you?",
        "what can you do",
        "what can you do?",
        "thank you",
        "thanks",
        "ok",
        "okay",
        "bye",
        "goodbye",
    }

    if text in general_phrases:
        return False

    # --------------------------------------------------------
    # General conversational questions
    # --------------------------------------------------------

    general_starts = (
        "hello ",
        "hi ",
        "hey ",
        "thanks ",
        "thank you ",
        "how are you ",
        "can you help me ",
        "tell me a joke",
        "what do you think",
        "explain generally",
    )

    if text.startswith(general_starts):
        return False

    # --------------------------------------------------------
    # Document-related signals
    # --------------------------------------------------------

    document_terms = (
        "document",
        "documents",
        "file",
        "files",
        "uploaded",
        "upload",
        "pdf",
        "docx",
        "txt",
        "report",
        "according to",
        "according to the document",
        "according to the file",
        "in the document",
        "in the file",
        "from the document",
        "from the file",
        "mentioned in",
        "written in",
        "shown in",
        "page ",
        "chapter ",
        "section ",
        "table ",
        "figure ",
        "record",
        "records",
    )

    if any(
        term in text
        for term in document_terms
    ):
        return True

    # --------------------------------------------------------
    # Structured information often stored in documents
    # --------------------------------------------------------

    structured_terms = (
        "roll number",
        "roll no",
        "registration number",
        "registration no",
        "student id",
        "student number",
        "exam date",
        "examination date",
        "exam schedule",
        "examination schedule",
        "practical exam",
        "practical examination",
        "written exam",
        "written examination",
        "course code",
        "project title",
        "project name",
    )

    if any(
        term in text
        for term in structured_terms
    ):
        return True

    # --------------------------------------------------------
    # Filename-like queries
    # --------------------------------------------------------

    if any(
        extension in text
        for extension in (
            ".pdf",
            ".docx",
            ".txt",
            ".pptx",
            ".xlsx",
            ".csv",
        )
    ):
        return True

    # --------------------------------------------------------
    # Default
    #
    # We currently prefer normal AI for ordinary questions.
    # RAG is activated by clear document-related signals.
    # --------------------------------------------------------

    return False


def _retrieve_documents(prompt: str):
    """
    Safely retrieve relevant documents.

    RAG failures should not break normal AI chat.
    """

    try:
        return search_documents(prompt)

    except Exception as exc:
        print(
            f"AI SERVICE RAG ERROR: {exc}"
        )

        return []


def chat_with_ai(
    prompt: str,
    system_prompt: str,
    model: str,
    temperature: int,
) -> str:
    """
    Hybrid AI chat.

    Normal questions:
        General AI response.

    Document-related questions:
        Retrieve relevant documents and include them as context.

    The same agent handles both modes.
    """

    prompt = (prompt or "").strip()

    if not prompt:
        return "Please enter a message."

    # ========================================================
    # Determine whether RAG should be used
    # ========================================================

    use_rag = _should_use_rag(prompt)

    print(
        f"AI SERVICE: use_rag={use_rag} "
        f"query={prompt!r}"
    )

    # ========================================================
    # Retrieve documents only when appropriate
    # ========================================================

    documents = []

    if use_rag:
        documents = _retrieve_documents(
            prompt
        )

    # ========================================================
    # Build document context
    # ========================================================

    context = "\n\n".join(
        document.page_content
        for document in documents
        if document.page_content
    )

    # ========================================================
    # Build hybrid prompt
    # ========================================================

    final_prompt = build_rag_prompt(
        question=prompt,
        context=context,
    )

    # ========================================================
    # Call Ollama
    # ========================================================

    response = ollama.chat(
        model=model,
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": final_prompt,
            },
        ],
        options={
            "temperature": temperature,
        },
    )

    return response["message"]["content"]