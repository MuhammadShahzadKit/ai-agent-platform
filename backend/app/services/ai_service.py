import ollama


def chat_with_ai(
    prompt: str,
    model: str,
    system_prompt: str,
    temperature: int,
) -> str:
    response = ollama.chat(
        model=model,
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        options={
            "temperature": temperature,
        },
    )

    return response["message"]["content"]