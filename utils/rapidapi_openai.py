"""
RapidAPI OpenAI wrapper - drop-in replacement for OpenAI client.
Uses RapidAPI's GPT-4 endpoint instead of direct OpenAI API.
"""

import os
from typing import List, Dict, Any
import httpx
from loguru import logger
from dotenv import load_dotenv

load_dotenv()


class RapidAPIOpenAI:
    """OpenAI-compatible client using RapidAPI."""

    def __init__(self):
        self.api_key = os.getenv("RAPIDAPI_KEY")
        self.host = os.getenv(
            "RAPIDAPI_OPENAI_HOST",
            "cheapest-gpt-4-turbo-gpt-4-vision-chatgpt-openai-ai-api.p.rapidapi.com",
        )
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o")
        self.base_url = f"https://{self.host}"

    async def create_completion(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 1000,
        temperature: float = 0.7,
    ) -> str:
        """Create chat completion via RapidAPI."""
        url = f"{self.base_url}/v1/chat/completions"

        payload = {
            "messages": messages,
            "model": self.model,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

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
            content = data["choices"][0]["message"]["content"]
            logger.debug(f"RapidAPI completion: {len(content)} chars")
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
        logger.info(f"RapidAPI OpenAI client initialized (model: {_client.model})")
    return _client
