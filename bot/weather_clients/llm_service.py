from aiogram.types import InlineKeyboardMarkup, Message, ReplyKeyboardMarkup
from bot.weather_clients.llm import (
    advice_cache_key,
    async_lru_cache,
    call_llm,
    extract_advice_text,
    get_payload,
)


@async_lru_cache(maxsize=128, key_builder=advice_cache_key)
async def get_llm_advice_text(
    message: Message,
    *,
    city: str,
    temp_c: int,
    description: str,
    user_data: dict | None = None,
):
    payload = await get_payload(
        message,
        city=city,
        temp_c=temp_c,
        description=description,
        user_data=user_data,
    )

    data_ai = await call_llm(payload)
    return extract_advice_text(data_ai)


async def send_llm_advice(
    message: Message,
    *,
    city: str,
    temp_c: int,
    description: str,
    reply_markup: ReplyKeyboardMarkup | InlineKeyboardMarkup | None = None,
    user_data: dict | None = None,
):
    advice_text = await get_llm_advice_text(
        message,
        city=city,
        temp_c=temp_c,
        description=description,
        user_data=user_data,
    )

    if advice_text:
        await message.answer(advice_text, reply_markup=reply_markup)

    return advice_text
