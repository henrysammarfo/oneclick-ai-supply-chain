from pathlib import Path
from dotenv import load_dotenv
import asyncio
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from utils.rapidapi_openai import get_openai_client


def main():
    load_dotenv(".env")

    async def run():
        client = get_openai_client()
        prompt = "Return a JSON array with exactly 2 components for a bicycle. Only JSON."
        try:
            response = await client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=120,
            )
            content = response if isinstance(response, str) else getattr(response, "choices", [""])[0].message.content
            print("LLM response:", content)
            try:
                json.loads(content)
                print("JSON parse: OK")
            except Exception:
                print("JSON parse: FAILED (check output)")
        except Exception as exc:
            print("LLM request failed:", exc)

    asyncio.run(run())


if __name__ == "__main__":
    main()
