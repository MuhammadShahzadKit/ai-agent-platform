from __future__ import annotations

import re
from pathlib import Path
from threading import Lock

from langchain_core.documents import Document

from app.services.rag.vector_store import get_vector_store


# ============================================================
# VECTOR STORE
# ============================================================

VECTOR_STORE = get_vector_store()


# ============================================================
# RETRIEVAL SETTINGS
# ============================================================

SEMANTIC_K = 12

# Maximum chunks returned to the LLM.
FINAL_K = 8

# For exact document questions, return more chunks so that
# information spread across a document is not missed.
EXACT_DOCUMENT_K = 12


# ============================================================
# CACHE
# ============================================================

# The complete Chroma collection is loaded into memory only once.
#
# This is important:
#
# OLD:
#     every query -> VECTOR_STORE.get(...)
#
# NEW:
#     first query -> load collection
#     later queries -> use memory
#
# This makes exact/keyword retrieval much faster.
# ============================================================

_DOCUMENT_CACHE: list[Document] | None = None

_CACHE_LOCK = Lock()


# ============================================================
# STOP WORDS
# ============================================================

STOP_WORDS = {
    "what",
    "is",
    "are",
    "the",
    "a",
    "an",
    "of",
    "in",
    "on",
    "to",
    "for",
    "does",
    "do",
    "have",
    "has",
    "when",
    "where",
    "which",
    "who",
    "and",
    "or",
    "with",
    "from",
    "this",
    "that",
    "these",
    "those",
    "give",
    "me",
    "tell",
    "about",
    "please",
    "can",
    "you",
    "their",
    "them",
    "include",
    "including",
    "every",
    "all",
}


# ============================================================
# NORMALIZATION
# ============================================================

def _normalize(text: str) -> str:
    """
    Normalize text for reliable matching.
    """

    text = str(text or "")

    text = text.lower()

    text = text.replace("_", " ")

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text.strip()


def _tokens(text: str) -> set[str]:
    """
    Extract searchable tokens.
    """

    words = re.findall(
        r"[a-zA-Z0-9][a-zA-Z0-9_\-]*",
        str(text).lower(),
    )

    return {
        word
        for word in words
        if word not in STOP_WORDS
        and len(word) >= 2
    }


# ============================================================
# QUERY EXTRACTION
# ============================================================

def _extract_page(query: str) -> int | None:
    """
    Detect:
        page 7
        page 3
        on page 5
    """

    match = re.search(
        r"\bpage\s+(\d+)\b",
        query,
        re.IGNORECASE,
    )

    if match:
        return int(match.group(1))

    return None


def _extract_filename(query: str) -> str | None:
    """
    Detect filenames such as:

        Shahzad.pdf
        Bismillah Tahir.pdf
        Bismillah_Tahir_clean.pdf
        report.docx
    """

    match = re.search(
        r"([A-Za-z0-9_\- ]+\.(?:pdf|docx|txt|pptx|xlsx|csv))\b",
        query,
        re.IGNORECASE,
    )

    if not match:
        return None

    return Path(
        match.group(1).strip()
    ).name.lower()


def _query_intent(query: str) -> dict:
    """
    Determine what kind of information the user is requesting.
    """

    q = _normalize(query)

    return {
        "roll_number": (
            "roll number" in q
            or "roll no" in q
            or "roll #" in q
        ),

        "written": (
            "written" in q
            or "written examination" in q
            or "written exam" in q
        ),

        "practical": (
            "practical" in q
            or "practicals" in q
            or "lab" in q
            or "laboratory" in q
        ),

        "date": (
            "date" in q
            or "when" in q
            or "schedule" in q
        ),

        "project": (
            "project title" in q
            or "project name" in q
            or "project" in q
        ),

        "page": (
            "page" in q
        ),

        "list": any(
            phrase in q
            for phrase in [
                "all",
                "subjects",
                "exams",
                "examinations",
                "dates",
                "schedule",
                "what are",
                "which are",
                "every",
                "including",
            ]
        ),
    }


# ============================================================
# DOCUMENT IDENTITY
# ============================================================

def _document_identity(document: Document) -> tuple:
    """
    Create a unique identity for a chunk.

    IMPORTANT:
    Do NOT use document_hash alone.

    Two files can contain exactly the same bytes and therefore
    have the same SHA256 hash while having different filenames.

    Example:

        2024-kik-40.pdf
        Bismillah Tahir.pdf

    Same content -> same hash
    Different files -> different filenames

    Therefore filename/source MUST participate in identity.
    """

    metadata = document.metadata or {}

    source = str(
        metadata.get(
            "source",
            "",
        )
    )

    filename = str(
        metadata.get(
            "filename",
            "",
        )
    )

    if not filename:
        filename = Path(source).name

    filename = Path(
        filename
    ).name.lower()

    page = metadata.get(
        "page",
        0,
    )

    chunk_index = metadata.get(
        "chunk_index",
        0,
    )

    chunk_id = metadata.get(
        "chunk_id"
    )

    if chunk_id:
        return (
            filename,
            str(chunk_id),
        )

    return (
        filename,
        page,
        chunk_index,
    )


# ============================================================
# LOAD DOCUMENT CACHE
# ============================================================

def _load_document_cache() -> list[Document]:
    """
    Load the entire indexed Chroma collection into memory.

    This happens only once per Python process.

    No embeddings are generated here.
    """

    global _DOCUMENT_CACHE

    if _DOCUMENT_CACHE is not None:
        return _DOCUMENT_CACHE

    with _CACHE_LOCK:

        if _DOCUMENT_CACHE is not None:
            return _DOCUMENT_CACHE

        print(
            "RAG: Loading document index into memory..."
        )

        data = VECTOR_STORE.get(
            include=[
                "documents",
                "metadatas",
            ]
        )

        documents = data.get(
            "documents"
        ) or []

        metadatas = data.get(
            "metadatas"
        ) or []

        result: list[Document] = []

        for text, metadata in zip(
            documents,
            metadatas,
        ):

            if not text:
                continue

            metadata = metadata or {}

            result.append(
                Document(
                    page_content=text,
                    metadata=metadata,
                )
            )

        _DOCUMENT_CACHE = result

        print(
            f"RAG: Indexed {len(result)} chunks in memory."
        )

        return _DOCUMENT_CACHE


# ============================================================
# CACHE RESET
# ============================================================

def clear_retrieval_cache() -> None:
    """
    Clear the in-memory retrieval cache.

    Call this after indexing new documents.
    """

    global _DOCUMENT_CACHE

    with _CACHE_LOCK:
        _DOCUMENT_CACHE = None

    print(
        "RAG: Retrieval cache cleared."
    )


# ============================================================
# EXACT TERM DETECTION
# ============================================================

def _contains_person_name(
    content: str,
    query: str,
) -> bool:
    """
    Detect important person-name overlap.

    This is especially useful for queries such as:

        What is Bismillah Tahir roll number?
        What are Bismillah Tahir practical exams?
    """

    query_tokens = _tokens(query)

    content_normalized = _normalize(
        content
    )

    # Names with two or more meaningful tokens.
    meaningful = [
        token
        for token in query_tokens
        if len(token) >= 3
    ]

    if len(meaningful) < 2:
        return False

    matches = sum(
        1
        for token in meaningful
        if re.search(
            rf"\b{re.escape(token)}\b",
            content_normalized,
        )
    )

    return matches >= 2


# ============================================================
# DATE DETECTION
# ============================================================

def _contains_date(text: str) -> bool:
    """
    Detect common examination date formats.
    """

    patterns = [
        r"\b\d{2}-\d{2}-\d{2}\b",
        r"\b\d{2}-\d{2}-\d{4}\b",
        r"\b\d{2}/\d{2}/\d{2}\b",
        r"\b\d{2}/\d{2}/\d{4}\b",
        r"\b\d{4}-\d{2}-\d{2}\b",
    ]

    return any(
        re.search(
            pattern,
            text,
        )
        for pattern in patterns
    )


# ============================================================
# LEXICAL SCORING
# ============================================================

def _lexical_score(
    document: Document,
    query: str,
) -> float:
    """
    Fast local lexical relevance scoring.

    This runs entirely in Python and does not call Ollama.
    """

    content = _normalize(
        document.page_content
    )

    query_normalized = _normalize(
        query
    )

    query_tokens = _tokens(
        query
    )

    content_tokens = _tokens(
        content
    )

    intent = _query_intent(
        query
    )

    score = 0.0

    # --------------------------------------------------------
    # Token overlap
    # --------------------------------------------------------

    if query_tokens:

        overlap = (
            query_tokens
            & content_tokens
        )

        score += (
            len(overlap)
            / max(
                len(query_tokens),
                1,
            )
        ) * 20.0

    # --------------------------------------------------------
    # Exact person-name matching
    # --------------------------------------------------------

    if _contains_person_name(
        content,
        query,
    ):
        score += 30.0

    # --------------------------------------------------------
    # Roll number
    # --------------------------------------------------------

    if intent["roll_number"]:

        if "roll number" in content:
            score += 100.0

        if "roll no" in content:
            score += 100.0

        if re.search(
            r"\broll\s*(?:number|no\.?)\b.{0,50}\d{4,}",
            content,
        ):
            score += 80.0

    # --------------------------------------------------------
    # Written examination
    # --------------------------------------------------------

    if intent["written"]:

        if "written examination" in content:
            score += 70.0

        elif "written exam" in content:
            score += 60.0

    # --------------------------------------------------------
    # Practical examination
    # --------------------------------------------------------

    if intent["practical"]:

        if "practical examination" in content:
            score += 90.0

        if "(lab)" in content:
            score += 70.0

        if " lab" in content:
            score += 35.0

        if re.search(
            r"\b[A-Z]{2,5}-\d{3}L\b",
            document.page_content,
        ):
            score += 40.0

    # --------------------------------------------------------
    # Dates
    # --------------------------------------------------------

    if intent["date"]:

        if _contains_date(
            document.page_content
        ):
            score += 35.0

    # --------------------------------------------------------
    # Project
    # --------------------------------------------------------

    if intent["project"]:

        if "project title" in content:
            score += 80.0

        if "project name" in content:
            score += 70.0

        if "bismillahcafeapp" in content:
            score += 70.0

    # --------------------------------------------------------
    # Course codes
    # --------------------------------------------------------

    course_codes = re.findall(
        r"\b[A-Z]{2,5}-\d{3}L?\b",
        query.upper(),
    )

    for course_code in course_codes:

        if course_code.lower() in content:
            score += 60.0

    # --------------------------------------------------------
    # Important course names
    # --------------------------------------------------------

    important_phrases = [
        "database systems",
        "data structures",
        "applied physics",
        "professional practices",
        "software engineering",
        "civics and community management",
    ]

    for phrase in important_phrases:

        if (
            phrase in query_normalized
            and phrase in content
        ):
            score += 50.0

    # --------------------------------------------------------
    # Filename matching
    # --------------------------------------------------------

    requested_filename = _extract_filename(
        query
    )

    if requested_filename:

        metadata = document.metadata or {}

        filename = str(
            metadata.get(
                "filename",
                metadata.get(
                    "source",
                    "",
                ),
            )
        )

        filename = Path(
            filename
        ).name.lower()

        if filename == requested_filename:
            score += 150.0

    return score


# ============================================================
# SEMANTIC SEARCH
# ============================================================

def _semantic_candidates(
    query: str,
) -> list[tuple[Document, float]]:
    """
    Semantic retrieval using Chroma.

    Used as one signal, not as the only retrieval method.
    """

    try:

        return VECTOR_STORE.similarity_search_with_score(
            query,
            k=SEMANTIC_K,
        )

    except Exception as exc:

        print(
            f"WARNING: semantic retrieval failed: {exc}"
        )

        return []


# ============================================================
# SEARCH
# ============================================================

def search_documents(
    query: str,
) -> list[Document]:
    """
    Hybrid retrieval engine.

    Strategy:

    1. Use semantic search for discovery.
    2. Use the cached document index for exact matching.
    3. Use lexical scoring for names, roll numbers,
       course codes, dates, practicals and filenames.
    4. Apply filename/page filters.
    5. Keep chunks from the same document together.
    6. Return the strongest relevant chunks.
    """

    query = query.strip()

    if not query:
        return []

    intent = _query_intent(
        query
    )

    requested_page = _extract_page(
        query
    )

    requested_filename = _extract_filename(
        query
    )

    # ========================================================
    # STEP 1
    # Load cached collection
    # ========================================================

    all_documents = _load_document_cache()

    if not all_documents:
        return []

    # ========================================================
    # STEP 2
    # Semantic retrieval
    # ========================================================

    semantic_results = _semantic_candidates(
        query
    )

    semantic_scores: dict[
        tuple,
        float
    ] = {}

    for document, distance in semantic_results:

        key = _document_identity(
            document
        )

        try:
            similarity = max(
                0.0,
                1.0 - float(distance),
            )
        except (
            TypeError,
            ValueError,
        ):
            similarity = 0.0

        semantic_scores[key] = max(
            semantic_scores.get(
                key,
                0.0,
            ),
            similarity,
        )

    # ========================================================
    # STEP 3
    # Determine exact-search mode
    # ========================================================

    exact_mode = (
        requested_page is not None
        or requested_filename is not None
        or intent["roll_number"]
        or intent["written"]
        or intent["practical"]
        or intent["project"]
        or intent["list"]
    )

    # ========================================================
    # STEP 4
    # Filename filtering
    # ========================================================

    candidate_documents = all_documents

    if requested_filename:

        filename_documents = []

        for document in candidate_documents:

            metadata = document.metadata or {}

            filename = str(
                metadata.get(
                    "filename",
                    metadata.get(
                        "source",
                        "",
                    ),
                )
            )

            filename = Path(
                filename
            ).name.lower()

            if filename == requested_filename:
                filename_documents.append(
                    document
                )

        if filename_documents:
            candidate_documents = (
                filename_documents
            )

    # ========================================================
    # STEP 5
    # Page filtering
    # ========================================================

    if requested_page is not None:

        page_documents = []

        for document in candidate_documents:

            try:
                page = int(
                    document.metadata.get(
                        "page",
                        0,
                    )
                )
            except (
                TypeError,
                ValueError,
            ):
                continue

            if page == requested_page:
                page_documents.append(
                    document
                )

        if page_documents:
            candidate_documents = (
                page_documents
            )

    # ========================================================
    # STEP 6
    # Score documents
    # ========================================================

    scored = []

    for document in candidate_documents:

        key = _document_identity(
            document
        )

        lexical = _lexical_score(
            document,
            query,
        )

        semantic = semantic_scores.get(
            key,
            0.0,
        )

        # Exact lexical information is more important than
        # semantic similarity for structured documents.
        final_score = (
            lexical
            + (
                semantic * 10.0
            )
        )

        scored.append(
            (
                document,
                final_score,
            )
        )

    # ========================================================
    # STEP 7
    # Sort
    # ========================================================

    scored.sort(
        key=lambda item: item[1],
        reverse=True,
    )

    # ========================================================
    # STEP 8
    # Structured exact questions
    #
    # For roll numbers, practical exams, written exams,
    # course schedules, etc., prefer chunks containing
    # explicit requested information.
    # ========================================================

    if exact_mode:

        # Keep all positively matching chunks first.
        positive = [
            item
            for item in scored
            if item[1] > 0
        ]

        if positive:
            scored = positive

    # ========================================================
    # STEP 9
    # Select results
    # ========================================================

    if intent["list"] or intent["practical"] or intent["written"]:

        limit = EXACT_DOCUMENT_K

    else:

        limit = 4

    selected = [
        document
        for document, _score in scored[
            :limit
        ]
    ]

    # ========================================================
    # STEP 10
    # Remove duplicate chunks
    # ========================================================

    final_documents = []

    seen = set()

    for document in selected:

        key = _document_identity(
            document
        )

        if key in seen:
            continue

        seen.add(key)

        final_documents.append(
            document
        )

    # ========================================================
    # STEP 11
    # Debug
    # ========================================================

    print(
        f"RETRIEVAL: query={query!r}"
    )

    print(
        f"RETRIEVAL: indexed={len(all_documents)}"
    )

    print(
        f"RETRIEVAL: candidates={len(candidate_documents)}"
    )

    print(
        f"RETRIEVAL: selected={len(final_documents)}"
    )

    for index, document in enumerate(
        final_documents,
        start=1,
    ):

        metadata = document.metadata or {}

        print(
            f"RETRIEVAL DOC {index}: "
            f"source={metadata.get('source')} "
            f"filename={metadata.get('filename')} "
            f"page={metadata.get('page')} "
            f"chunk={metadata.get('chunk_index')}"
        )

    return final_documents