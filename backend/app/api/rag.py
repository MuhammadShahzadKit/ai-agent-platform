from __future__ import annotations

import os
import shutil

from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel, Field

from app.services.rag.index_service import index_document
from app.services.rag.rag_service import ask_rag


# ============================================================
# ROUTER
# ============================================================

router = APIRouter(
    prefix="/rag",
    tags=["RAG"],
)


# ============================================================
# UPLOAD DIRECTORY
# ============================================================

UPLOAD_DIR = "uploads"

os.makedirs(
    UPLOAD_DIR,
    exist_ok=True,
)


# ============================================================
# REQUEST SCHEMA
# ============================================================

class RAGQueryRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        description="Question to ask about uploaded documents.",
    )


# ============================================================
# UPLOAD DOCUMENT
# ============================================================

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
):
    """
    Upload a document and index it into the RAG system.
    """

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Filename is required.",
        )

    filename = os.path.basename(
        file.filename
    )

    file_path = os.path.join(
        UPLOAD_DIR,
        filename,
    )

    try:

        with open(
            file_path,
            "wb",
        ) as buffer:

            shutil.copyfileobj(
                file.file,
                buffer,
            )

        print(
            f"RAG API: Uploaded {filename}"
        )

        result = index_document(
            file_path,
        )

        return {
            "success": True,
            "filename": filename,
            **result,
            "message": (
                "Document uploaded and indexed successfully."
            ),
        }

    except Exception as exc:

        print(
            f"RAG API ERROR: {exc}"
        )

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


# ============================================================
# ASK RAG
# ============================================================

@router.post("/query")
async def query_rag(
    request: RAGQueryRequest,
):
    """
    Ask a question about the indexed documents.
    """

    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty.",
        )

    try:

        print(
            f"RAG API: Question = {question}"
        )

        answer = ask_rag(
            question
        )

        return {
            "success": True,
            "question": question,
            "answer": answer,
        }

    except Exception as exc:

        print(
            f"RAG API QUERY ERROR: {exc}"
        )

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )