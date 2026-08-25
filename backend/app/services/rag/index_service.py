from __future__ import annotations

import hashlib
import json
from pathlib import Path

from langchain_core.documents import Document

from app.services.rag.document_loader import load_document
from app.services.rag.text_splitter import split_documents
from app.services.rag.vector_store import get_vector_store


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[3]

STORAGE_DIR = BASE_DIR / "storage"
MANIFEST_PATH = STORAGE_DIR / "document_manifest.json"

STORAGE_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# ============================================================
# SUPPORTED FILE TYPES
# ============================================================

SUPPORTED_EXTENSIONS = {
    ".pdf",
    ".docx",
    ".doc",
    ".txt",
    ".md",
    ".csv",
    ".xlsx",
    ".xls",
    ".pptx",
    ".ppt",
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
    ".bmp",
    ".tiff",
    ".tif",
}


# ============================================================
# MANIFEST
# ============================================================

def _load_manifest() -> dict:
    if not MANIFEST_PATH.exists():
        return {}

    try:
        return json.loads(
            MANIFEST_PATH.read_text(
                encoding="utf-8"
            )
        )

    except Exception as exc:

        print(
            f"WARNING: Could not load manifest: {exc}"
        )

        return {}


def _save_manifest(
    manifest: dict,
) -> None:

    MANIFEST_PATH.write_text(
        json.dumps(
            manifest,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


# ============================================================
# SHA-256
# ============================================================

def _file_hash(
    file_path: str,
) -> str:
    """
    Calculate SHA-256 using streaming reads.
    """

    sha256 = hashlib.sha256()

    with open(
        file_path,
        "rb",
    ) as file:

        while True:

            block = file.read(
                1024 * 1024
            )

            if not block:
                break

            sha256.update(block)

    return sha256.hexdigest()


# ============================================================
# DOCUMENT ID
# ============================================================

def _document_id(
    document_hash: str,
) -> str:
    """
    The file content hash is the logical document identity.
    """

    return document_hash


# ============================================================
# CHUNK ID
# ============================================================

def _chunk_id(
    document_id: str,
    location_type: str,
    location: str | int,
    chunk_index: int,
) -> str:
    """
    Create a deterministic ID for one retrieval chunk.

    location_type + location are included because one source
    document can contain multiple independent sections.

    Example for DOCX:

        paragraphs / 1 / 0
        table / 1 / 0

    These must produce different IDs.
    """

    raw = (
        f"{document_id}:"
        f"{location_type}:"
        f"{location}:"
        f"{chunk_index}"
    )

    return hashlib.sha256(
        raw.encode("utf-8")
    ).hexdigest()


# ============================================================
# PREPARE METADATA
# ============================================================

def _prepare_chunk_metadata(
    chunk: Document,
    path: Path,
    document_hash: str,
    document_id: str,
) -> dict:

    metadata = dict(
        chunk.metadata or {}
    )

    # --------------------------------------------------------
    # Location type
    # --------------------------------------------------------

    location_type = str(
        metadata.get(
            "location_type",
            "document",
        )
    )

    # --------------------------------------------------------
    # Location
    # --------------------------------------------------------

    location = metadata.get(
        "location",
        1,
    )

    # --------------------------------------------------------
    # Page
    #
    # Keep page available for compatibility with existing
    # retrieval code.
    # --------------------------------------------------------

    try:

        page = int(
            metadata.get(
                "page",
                location
                if isinstance(location, int)
                else 1,
            )
        )

    except (
        TypeError,
        ValueError,
    ):

        page = 1

    # --------------------------------------------------------
    # Chunk index
    # --------------------------------------------------------

    try:

        chunk_index = int(
            metadata.get(
                "chunk_index",
                0,
            )
        )

    except (
        TypeError,
        ValueError,
    ):

        chunk_index = 0

    # --------------------------------------------------------
    # Stable chunk ID
    # --------------------------------------------------------

    chunk_id = _chunk_id(
        document_id=document_id,
        location_type=location_type,
        location=location,
        chunk_index=chunk_index,
    )

    # --------------------------------------------------------
    # Standard metadata
    # --------------------------------------------------------

    metadata.update(
        {
            "filename": path.name,
            "source": str(path),
            "file_type": path.suffix.lower(),
            "document_hash": document_hash,
            "document_id": document_id,
            "page": page,
            "chunk_index": chunk_index,
            "chunk_id": chunk_id,
            "location_type": location_type,
            "location": location,
        }
    )

    return metadata


# ============================================================
# INDEX ONE DOCUMENT
# ============================================================

def index_document(
    file_path: str,
    force: bool = False,
) -> dict:

    path = Path(
        file_path
    )

    if not path.exists():

        raise FileNotFoundError(
            f"File not found: {file_path}"
        )

    if not path.is_file():

        raise ValueError(
            f"Path is not a file: {file_path}"
        )

    extension = path.suffix.lower()

    if extension not in SUPPORTED_EXTENSIONS:

        return {
            "status": "unsupported",
            "filename": path.name,
            "extension": extension,
            "chunks": 0,
        }

    # ========================================================
    # HASH FIRST
    # ========================================================

    document_hash = _file_hash(
        str(path)
    )

    document_id = _document_id(
        document_hash
    )

    manifest = _load_manifest()

    # ========================================================
    # DUPLICATE CONTENT DETECTION
    # ========================================================

    existing = manifest.get(
        document_id
    )

    if existing and not force:

        filenames = existing.get(
            "filenames",
            [],
        )

        if path.name not in filenames:

            filenames.append(
                path.name
            )

            existing["filenames"] = filenames

            _save_manifest(
                manifest
            )

            print(
                "RAG: Duplicate content detected."
            )

            print(
                f"RAG: Existing document: "
                f"{filenames[0]}"
            )

            print(
                f"RAG: New filename: "
                f"{path.name}"
            )

            print(
                "RAG: Reusing existing indexed document."
            )

        return {
            "status": "already_indexed",
            "filename": path.name,
            "document_id": document_id,
            "document_hash": document_hash,
            "chunks": existing.get(
                "chunks",
                0,
            ),
            "duplicate": True,
        }

    # ========================================================
    # LOAD
    # ========================================================

    print(
        f"RAG: Loading {path.name}..."
    )

    documents = load_document(
        str(path)
    )

    if not documents:

        return {
            "status": "empty",
            "filename": path.name,
            "document_id": document_id,
            "document_hash": document_hash,
            "chunks": 0,
        }

    print(
        f"RAG: Loaded {len(documents)} document sections."
    )

    # ========================================================
    # SPLIT
    # ========================================================

    chunks = split_documents(
        documents
    )

    if not chunks:

        return {
            "status": "empty",
            "filename": path.name,
            "document_id": document_id,
            "document_hash": document_hash,
            "chunks": 0,
        }

    print(
        f"RAG: Created {len(chunks)} chunks."
    )

    # ========================================================
    # VECTOR STORE
    # ========================================================

    vector_store = get_vector_store()

    ids: list[str] = []

    valid_chunks: list[Document] = []

    seen_ids: set[str] = set()

    for chunk in chunks:

        metadata = _prepare_chunk_metadata(
            chunk=chunk,
            path=path,
            document_hash=document_hash,
            document_id=document_id,
        )

        chunk.metadata = metadata

        chunk_id = metadata["chunk_id"]

        # ----------------------------------------------------
        # Defensive duplicate protection
        # ----------------------------------------------------

        if chunk_id in seen_ids:

            raw = (
                f"{chunk_id}:"
                f"{len(valid_chunks)}"
            )

            chunk_id = hashlib.sha256(
                raw.encode("utf-8")
            ).hexdigest()

            metadata["chunk_id"] = chunk_id

        seen_ids.add(
            chunk_id
        )

        ids.append(
            chunk_id
        )

        valid_chunks.append(
            chunk
        )

    # ========================================================
    # INDEX
    # ========================================================

    if valid_chunks:

        print(
            f"RAG: Embedding/indexing "
            f"{len(valid_chunks)} chunks..."
        )

        vector_store.add_documents(
            documents=valid_chunks,
            ids=ids,
        )

    # ========================================================
    # MANIFEST
    # ========================================================

    manifest[document_id] = {
        "document_id": document_id,
        "document_hash": document_hash,
        "filenames": [
            path.name
        ],
        "source": str(path),
        "file_type": extension,
        "chunks": len(valid_chunks),
    }

    _save_manifest(
        manifest
    )

    # ========================================================
    # CLEAR RETRIEVAL CACHE
    # ========================================================

    try:

        from app.services.rag.retrieval_service import (
            clear_retrieval_cache,
        )

        clear_retrieval_cache()

    except Exception as exc:

        print(
            f"WARNING: Could not clear retrieval cache: {exc}"
        )

    return {
        "status": "indexed",
        "filename": path.name,
        "document_id": document_id,
        "document_hash": document_hash,
        "chunks": len(valid_chunks),
        "duplicate": False,
    }


# ============================================================
# INDEX UPLOAD DIRECTORY
# ============================================================

def index_upload_directory(
    upload_directory: str = "uploads",
    force: bool = False,
) -> list[dict]:

    upload_path = Path(
        upload_directory
    )

    if not upload_path.exists():

        print(
            f"RAG: Upload directory not found: "
            f"{upload_path}"
        )

        return []

    results = []

    for file_path in sorted(
        upload_path.iterdir()
    ):

        if not file_path.is_file():
            continue

        extension = (
            file_path.suffix.lower()
        )

        if extension not in SUPPORTED_EXTENSIONS:

            results.append(
                {
                    "status": "unsupported",
                    "filename": file_path.name,
                    "extension": extension,
                    "chunks": 0,
                }
            )

            continue

        try:

            result = index_document(
                str(file_path),
                force=force,
            )

            results.append(
                result
            )

        except Exception as exc:

            print(
                f"ERROR: Failed to index "
                f"{file_path.name}: {exc}"
            )

            results.append(
                {
                    "status": "error",
                    "filename": file_path.name,
                    "error": str(exc),
                    "chunks": 0,
                }
            )

    return results