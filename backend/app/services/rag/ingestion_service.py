from pathlib import Path

from langchain_core.documents import Document
from langchain_community.document_loaders import (
    TextLoader,
    Docx2txtLoader,
)

from app.services.rag.document_loader import load_document
from app.services.rag.text_splitter import split_documents
from app.services.rag.vector_store import get_vector_store


def ingest_document(file_path: str):
    """
    Load, split, and index a document into the vector store.
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Document not found: {file_path}"
        )

    print("\n==========================")
    print("INGESTING DOCUMENT")
    print("==========================")
    print(f"File: {file_path}")

    # Load document/pages
    documents = load_document(file_path)

    print(f"Loaded documents/pages: {len(documents)}")

    # Split into chunks
    chunks = split_documents(documents)

    print(f"Created chunks: {len(chunks)}")

    # Store embeddings
    vector_store = get_vector_store()
    vector_store.add_documents(chunks)

    print("Documents successfully indexed.")
    print("==========================\n")

    return len(chunks)