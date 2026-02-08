"""
RapidAPI LLM wrapper - drop-in replacement for OpenAI client.
Supports multiple RapidAPI providers via RAPIDAPI_PROVIDER.
"""

import os
import json
from typing import List, Dict, Any, Tuple
import httpx
from loguru import logger
from dotenv import load_dotenv

load_dotenv()


class RapidAPIOpenAI:
    """OpenAI-compatible client using RapidAPI."""

    def __init__(self):
        self.api_key = os.getenv("RAPIDAPI_KEY")
        self.provider = os.getenv("RAPIDAPI_PROVIDER", "chat-gpt26").strip().lower()
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o")
        self.alt_model = os.getenv("RAPIDAPI_LLM_MODEL", "GPT-5-mini")

        default_host = "cheapest-gpt-4-turbo-gpt-4-vision-chatgpt-openai-ai-api.p.rapidapi.com"
        if self.provider == "chat-gpt26":
            default_host = "chat-gpt26.p.rapidapi.com"
        elif self.provider == "open-ai21":
            default_host = "open-ai21.p.rapidapi.com"

        self.host = os.getenv("RAPIDAPI_OPENAI_HOST", default_host)
        self.base_url = f"https://{self.host}"

    def _build_request(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int,
        temperature: float,
    ) -> Tuple[str, Dict[str, Any]]:
        if self.provider == "open-ai21":
            url = f"{self.base_url}/conversationllama"
            payload = {"messages": messages, "web_access": False}
            return url, payload
        if self.provider == "chat-gpt26":
            url = f"{self.base_url}/"
            payload = {"model": self.alt_model, "messages": messages}
            return url, payload

        url = f"{self.base_url}/v1/chat/completions"
        payload = {
            "messages": messages,
            "model": self.model,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        return url, payload

    @staticmethod
    def _extract_text(data: Any) -> str:
        if isinstance(data, str):
            return data
        if isinstance(data, dict):
            if "choices" in data and data["choices"]:
                return data["choices"][0]["message"]["content"]
            for key in ("result", "response", "text", "output"):
                if key in data:
                    return str(data[key])
        return json.dumps(data)

    async def create_completion(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 1000,
        temperature: float = 0.7,
    ) -> str:
        """Create chat completion via RapidAPI."""
        url, payload = self._build_request(messages, max_tokens, temperature)

        headers = {
            "x-rapidapi-key": self.api_key,
            "x-rapidapi-host": self.host,
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                url, json=payload, headers=headers, timeout=30.0
            )
            response.raise_for_status()
            data = response.json()
            content = self._extract_text(data)
            logger.info(f"RapidAPI completion ({self.provider}): {len(content)} chars")
            return content

    class _ChatCompletions:
        """Nested class matching OpenAI SDK structure."""

        def __init__(self, parent: "RapidAPIOpenAI"):
            self._parent = parent

        async def create(
            self,
            messages: List[Dict[str, str]],
            model: str = None,
            max_tokens: int = 1000,
            temperature: float = 0.7,
            **kwargs,
        ) -> str:
            """Match OpenAI SDK chat.completions.create() interface.
            Returns content string directly (not a response object)."""
            return await self._parent.create_completion(
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
            )

    class _Chat:
        def __init__(self, parent: "RapidAPIOpenAI"):
            self.completions = RapidAPIOpenAI._ChatCompletions(parent)

    @property
    def chat(self) -> "_Chat":
        """Match OpenAI SDK client.chat.completions structure."""
        return RapidAPIOpenAI._Chat(self)


_client = None


def get_openai_client() -> RapidAPIOpenAI:
    """Get singleton RapidAPI OpenAI client."""
    global _client
    if _client is None:
        _client = RapidAPIOpenAI()
        logger.info(
            f"RapidAPI client initialized (provider: {_client.provider}, host: {_client.host})"
        )
    return _client
