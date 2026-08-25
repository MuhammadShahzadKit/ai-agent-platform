from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.conversation import Conversation
from app.models.user import User
from app.services.agent_service import get_agent
from app.services.ai_service import chat_with_ai
from app.services.rag.retrieval_service import search_documents


router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)


class ChatRequest(BaseModel):
    message: str


@router.post("/{agent_id}")
def chat(
    agent_id: int,
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # --------------------------------------------------------
    # Validate message
    # --------------------------------------------------------

    message = request.message.strip()

    if not message:
        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty.",
        )

    # --------------------------------------------------------
    # Get agent
    # --------------------------------------------------------

    agent = get_agent(
        db,
        agent_id,
        current_user.id,
    )

    if not agent:
        raise HTTPException(
            status_code=404,
            detail="Agent not found",
        )

    # --------------------------------------------------------
    # Conversation history
    # --------------------------------------------------------

    conversations = (
        db.query(Conversation)
        .filter(
            Conversation.agent_id == agent_id
        )
        .order_by(
            Conversation.id
        )
        .all()
    )

    history_parts: list[str] = []

    for conversation in conversations:
        history_parts.append(
            f"User: {conversation.user_message}"
        )

        history_parts.append(
            f"Assistant: {conversation.ai_response}"
        )

    history = "\n".join(history_parts)

    # --------------------------------------------------------
    # RAG DOCUMENT RETRIEVAL
    #
    # Only search documents when this agent has use_rag=True.
    # --------------------------------------------------------

    document_context = ""

    if agent.use_rag:

        try:
            documents = search_documents(message)

        except Exception as exc:
            print(
                f"CHAT RAG ERROR: {exc}"
            )

            documents = []

        document_parts: list[str] = []

        for index, document in enumerate(
            documents,
            start=1,
        ):
            metadata = (
                document.metadata
                or {}
            )

            filename = metadata.get(
                "filename",
                "unknown",
            )

            page = metadata.get(
                "page",
                "unknown",
            )

            document_parts.append(
                f"[DOCUMENT {index}]\n"
                f"FILE: {filename}\n"
                f"PAGE: {page}\n"
                f"CONTENT:\n"
                f"{document.page_content}"
            )

        document_context = "\n\n".join(
            document_parts
        )

    # --------------------------------------------------------
    # Build document instructions
    # --------------------------------------------------------

    if agent.use_rag:

        if document_context:

            document_instruction = """
This agent is configured as a document-aware RAG agent.

Use the Relevant Documents as the primary source of
factual information when they contain information related
to the user's question.

Do not invent document-specific facts.
"""

        else:

            document_instruction = """
This agent is configured as a document-aware RAG agent.

No relevant uploaded document was found for this question.

If the user asks for information that specifically requires
the uploaded documents, clearly state that the information
was not found in the available documents.

Do not pretend that information came from a document.
"""

    else:

        document_instruction = """
This agent is configured as a general AI assistant.

Do NOT require uploaded documents to answer the user.

Answer normal questions using your general AI capabilities
and the agent's system instructions.

Uploaded documents are not required for this agent.
"""

    # --------------------------------------------------------
    # Build prompt
    # --------------------------------------------------------

    full_prompt = f"""
You are an AI assistant operating inside an AI Agent Platform.

AGENT SYSTEM INSTRUCTIONS:
{agent.system_prompt}

AGENT RAG MODE:
{agent.use_rag}

{document_instruction}

RELEVANT DOCUMENTS:
{document_context}

CONVERSATION HISTORY:
{history}

USER:
{message}

RESPONSE RULES:

1. Follow the agent's system instructions.

2. If RAG mode is enabled, use relevant uploaded documents
   when they contain information needed for the answer.

3. If RAG mode is disabled, answer normally without requiring
   uploaded documents.

4. Preserve names, numbers, dates, codes and other factual
   details exactly when supported by the available context.

5. Do not invent document-specific information.

6. Give a direct and useful answer.

ASSISTANT:
"""

    # --------------------------------------------------------
    # Generate AI response
    # --------------------------------------------------------

    try:

        response = chat_with_ai(
            prompt=full_prompt,
            model=agent.model,
            system_prompt=agent.system_prompt,
            temperature=agent.temperature,
        )

    except Exception as exc:

        print(
            f"CHAT AI ERROR: {exc}"
        )

        raise HTTPException(
            status_code=500,
            detail=f"AI response failed: {exc}",
        )

    # --------------------------------------------------------
    # Save conversation
    # --------------------------------------------------------

    conversation = Conversation(
        title=message[:50],
        user_message=message,
        ai_response=response,
        agent_id=agent.id,
    )

    db.add(conversation)

    db.commit()

    db.refresh(conversation)

    # --------------------------------------------------------
    # Response
    # --------------------------------------------------------

    return {
        "success": True,
        "agent": agent.name,
        "use_rag": agent.use_rag,
        "response": response,
        "conversation_id": conversation.id,
    }