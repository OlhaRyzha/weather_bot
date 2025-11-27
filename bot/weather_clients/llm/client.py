import aiohttp
from config.settings import LLM_URL


async def call_llm(payload: dict[str, str]):
    if not LLM_URL:
        return None

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{LLM_URL}/api/generate", json=payload) as resp:
                if resp.status != 200:
                    return None
                return await resp.json()
    except aiohttp.ClientError:
        return None
