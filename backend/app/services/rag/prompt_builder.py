def build_rag_prompt(
    context: str,
    question: str,
) -> str:
    """
    Build a hybrid AI prompt.

    The agent can answer normal questions using its general
    knowledge. When relevant document context is available,
    the agent should use that information as an additional
    factual source.

    IMPORTANT:
    The presence of document context does NOT mean every
    question must be answered only from the document.
    """

    context = (context or "").strip()
    question = (question or "").strip()

    if context:
        document_section = f"""
RELEVANT DOCUMENT CONTEXT

The following information was retrieved from the user's
uploaded documents because it may be relevant to the question.

Use this information when it is relevant and supported.

Do not claim that information came from a document if it
was not provided below.

Do not ignore your general reasoning ability. You may explain,
summarize, interpret, or clarify the document information when
appropriate.

--- DOCUMENT CONTEXT ---

{context}

--- END DOCUMENT CONTEXT ---
"""

    else:
        document_section = """
RELEVANT DOCUMENT CONTEXT

No relevant uploaded document was found for this question.

Answer the user's question normally using your general AI
knowledge and the agent's instructions.

Do NOT say that the information could not be found in an
uploaded document unless the user explicitly asked about an
uploaded document.
"""

    return f"""
You are an AI assistant operating inside an AI Agent Platform.

You have two capabilities:

1. General AI knowledge and reasoning.
2. Access to relevant information from uploaded documents
   when document context is provided.

IMPORTANT BEHAVIOR:

- Do NOT assume every question is about an uploaded document.
- For greetings, casual conversation, general knowledge,
  explanations, reasoning, and other normal questions, answer
  normally.
- When relevant document context is provided, use it when it
  helps answer the user's question.
- If the user asks specifically about information contained in
  an uploaded document, prioritize the provided document
  context.
- Never invent facts and present them as coming from a document.
- If the document context does not contain the requested
  information, you may use general knowledge when the question
  allows it.
- If the user explicitly asks for an answer strictly according
  to a document and the information is not available, clearly
  state that the document does not provide the requested
  information.

{document_section}

USER QUESTION

{question}

RESPONSE:

Provide a direct, useful answer.
"""