import requests


OLLAMA_URL = "http://localhost:11434/api/chat"


def ask_ollama(
    model: str,
    messages: list,
):
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": model,
            "messages": messages,
            "stream": False,
        },
        timeout=300,
    )

    response.raise_for_status()

    data = response.json()

    return data["message"]["content"]