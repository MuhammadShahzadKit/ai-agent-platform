from __future__ import annotations

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


# ---------------------------------------------------------
# Chunking configuration
# ---------------------------------------------------------
#
# 1000 characters is large enough to preserve useful context
# while keeping retrieval reasonably precise.
#
# The overlap prevents important information from being cut
# exactly at a chunk boundary.
#

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150


_SPLITTER = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
    separators=[
        "\n\n",
        "\n",
        ". ",
        "? ",
        "! ",
        " ",
        "",
    ],
    length_function=len,
    is_separator_regex=False,
)


def _clean_text(text: str) -> str:
    """
    Normalize obvious PDF extraction noise without destroying
    the structure of the document.
    """

    if not text:
        return ""

    # Normalize different newline styles.
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    # Remove trailing whitespace from every line.
    lines = [
        line.rstrip()
        for line in text.split("\n")
    ]

    # Remove excessive blank lines.
    cleaned_lines: list[str] = []
    previous_blank = False

    for line in lines:

        if not line.strip():

            if previous_blank:
                continue

            previous_blank = True
            cleaned_lines.append("")

        else:

            previous_blank = False
            cleaned_lines.append(line)

    return "\n".join(cleaned_lines).strip()


def split_documents(
    documents: list[Document],
) -> list[Document]:
    """
    Split page-level Documents into retrieval chunks.

    Important:
    - Page number is preserved.
    - Source/filename metadata is preserved.
    - Each chunk receives a deterministic chunk_index.
    - No embeddings are generated here.
    """

    chunks: list[Document] = []

    for document in documents:

        text = _clean_text(
            document.page_content
        )

        if not text:
            continue

        # Create chunks from ONE page at a time.
        #
        # This is intentional because page-level questions such
        # as "What is on page 7?" should remain possible later.
        page_chunks = _SPLITTER.split_text(
            text
        )

        # Remove empty chunks.
        page_chunks = [
            chunk.strip()
            for chunk in page_chunks
            if chunk.strip()
        ]

        total_chunks = len(page_chunks)

        for index, chunk_text in enumerate(
            page_chunks
        ):

            metadata = dict(
                document.metadata
            )

            metadata.update(
                {
                    "chunk_index": index,
                    "total_chunks": total_chunks,
                    "content_type": metadata.get(
                        "content_type",
                        "text",
                    ),
                }
            )

            chunks.append(
                Document(
                    page_content=chunk_text,
                    metadata=metadata,
                )
            )

    return chunks
