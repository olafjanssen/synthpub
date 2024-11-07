import asyncio
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

from ai_curator.llm.ollama_client import OllamaClient
import httpx


async def main():
    client = OllamaClient()

    try:
        content = await client.generate("Hello, world!", timeout=30.0)
        print(content)
    except httpx.ReadTimeout:
        print("The request timed out. Please try again later.")

if __name__ == '__main__':
    asyncio.run(main())
