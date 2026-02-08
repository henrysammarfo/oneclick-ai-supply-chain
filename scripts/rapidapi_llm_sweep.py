from pathlib import Path
from dotenv import load_dotenv
import asyncio
import json
import os
import sys

import httpx


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

load_dotenv(".env")


PROVIDERS = [
    {
        "name": "openai-rapid",
        "host": "cheapest-gpt-4-turbo-gpt-4-vision-chatgpt-openai-ai-api.p.rapidapi.com",
        "path": "/v1/chat/completions",
        "payload": lambda prompt: {
            "model": os.getenv("OPENAI_MODEL", "gpt-4o"),
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2,
            "max_tokens": 120,
        },
    },
    {
        "name": "open-ai21",
        "host": "open-ai21.p.rapidapi.com",
        "path": "/conversationllama",
        "payload": lambda prompt: {
            "messages": [{"role": "user", "content": prompt}],
            "web_access": False,
        },
    },
    {
        "name": "chat-gpt26",
        "host": "chat-gpt26.p.rapidapi.com",
        "path": "/",
        "payload": lambda prompt: {
            "model": os.getenv("RAPIDAPI_LLM_MODEL", "GPT-5-mini"),
            "messages": [{"role": "user", "content": prompt}],
        },
    },
]


def extract_text(data):
    if isinstance(data, dict):
        if "choices" in data and data["choices"]:
            return data["choices"][0]["message"]["content"]
        for key in ("result", "response", "text", "output"):
            if key in data:
                return str(data[key])
    return json.dumps(data)[:200]


async def test_provider(client, provider, prompt):
    url = f"https://{provider['host']}{provider['path']}"
    headers = {
        "x-rapidapi-key": os.getenv("RAPIDAPI_KEY", ""),
        "x-rapidapi-host": provider["host"],
        "Content-Type": "application/json",
    }
    try:
        resp = await client.post(url, json=provider["payload"](prompt), headers=headers, timeout=30.0)
        status = resp.status_code
        if status != 200:
            return provider["name"], status, None, resp.text[:200]
        data = resp.json()
        return provider["name"], status, extract_text(data), None
    except Exception as exc:
        return provider["name"], None, None, str(exc)


async def main():
    prompt = "Return a JSON array with exactly 2 components for a bicycle. Only JSON."
    async with httpx.AsyncClient() as client:
        for p in PROVIDERS:
            name, status, text, err = await test_provider(client, p, prompt)
            if status == 200:
                print(f"{name}: OK (200)")
                print(f"sample: {text}")
            else:
                print(f"{name}: FAIL ({status}) {err}")


if __name__ == "__main__":
    asyncio.run(main())
