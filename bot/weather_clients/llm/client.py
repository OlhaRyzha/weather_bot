import aiohttp
from typing import Dict

from config.settings import LLM_URL, LLM_API_TOKEN


async def call_llm(payload: Dict[str, str]):

    if not LLM_URL or not LLM_API_TOKEN:
        return None

    headers = {
        "Authorization": f"Bearer {LLM_API_TOKEN}",
        "Content-Type": "application/json",
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(LLM_URL, json=payload, headers=headers) as resp:
                if resp.status != 200:
                    return None
                return await resp.json()
    except aiohttp.ClientError:
        return None
