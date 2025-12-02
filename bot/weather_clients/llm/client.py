import aiohttp
import logging
import ssl
from typing import Dict

import certifi
from config.settings import LLM_URL, LLM_API_TOKEN

logger = logging.getLogger(__name__)
_SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())


async def call_llm(payload: Dict[str, str]):

    if not LLM_URL or not LLM_API_TOKEN:
        logger.warning("LLM config missing, skipping request")
        return None

    headers = {
        "Authorization": f"Bearer {LLM_API_TOKEN}",
        "Content-Type": "application/json",
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                LLM_URL, json=payload, headers=headers, ssl=_SSL_CONTEXT
            ) as resp:
                logger.info("LLM response status: %s", resp.status)
                if resp.status != 200:
                    detail: str | None = None
                    try:
                        detail = await resp.text()
                    except Exception:
                        detail = None

                    if detail:
                        snippet = detail[:500].replace("\n", " ")
                        logger.warning(
                            "LLM request failed with status %s: %s",
                            resp.status,
                            snippet,
                        )
                    else:
                        logger.warning("LLM request failed with status %s", resp.status)
                    return None
                return await resp.json()
    except aiohttp.ClientError as exc:
        logger.exception("LLM request errored: %s", exc)
        return None
