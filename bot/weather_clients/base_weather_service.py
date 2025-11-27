import contextlib
import ssl
import aiohttp
import certifi
from aiogram.types import (
    FSInputFile,
    InlineKeyboardMarkup,
    Message,
    ReplyKeyboardMarkup,
)
from bot.helpers import format_temperature_message, get_icon_key, resolve_icon_path
from bot.weather_clients.llm_service import get_llm_advice_text

from config.settings import (
    DEFAULT_UNITS,
    MESSAGES,
    WEATHER_API_BASE,
    WEATHER_API_TOKEN,
)
from config.types import QueryParamType

_SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())


async def perform_request(params: QueryParamType):
    async with aiohttp.ClientSession() as session:
        async with session.get(
            WEATHER_API_BASE, params=params, ssl=_SSL_CONTEXT
        ) as response:
            if response.status != 200:
                return None
            return await response.json()


def build_caption_payload(
    data,
    fallback_city: str | None = None,
    display_name: str | None = None,
):
    city_name = display_name or data.get("name") or fallback_city or "Unknown location"
    main = data.get("main", {})
    weather = (data.get("weather") or [{}])[0]
    temp = int(round(main.get("temp", 0)))
    description = str(weather.get("description", ""))
    caption = format_temperature_message(city_name, temp, description)

    weather_id = int(weather.get("id") or 0)
    icon_key = get_icon_key(weather_id)
    icon_path = resolve_icon_path(icon_key)
    return caption, icon_path, city_name, temp, description


async def send_weather_response(
    message: Message,
    *,
    query_params: QueryParamType,
    fallback_city: str | None = None,
    display_name: str | None = None,
    reply_markup: ReplyKeyboardMarkup | InlineKeyboardMarkup | None = None,
):
    if not WEATHER_API_TOKEN or not WEATHER_API_BASE:
        await message.answer(
            MESSAGES["weather_api_not_configured"], reply_markup=reply_markup
        )
        return

    params = dict(query_params)
    params.setdefault("units", DEFAULT_UNITS)
    params["appid"] = WEATHER_API_TOKEN

    try:
        data = await perform_request(params)
    except aiohttp.ClientError:
        data = None

    if not data:
        await message.answer(MESSAGES["city_not_found"], reply_markup=reply_markup)
        return

    caption, icon_path, city_name, temp, description = build_caption_payload(
        data,
        fallback_city=fallback_city,
        display_name=display_name,
    )

    loader_message = None
    loader_text = MESSAGES.get("loader_message")
    if loader_text:
        loader_message = await message.answer(loader_text)

    advice_text = await get_llm_advice_text(
        message,
        city=city_name,
        temp_c=temp,
        description=description,
        user_data={"units": DEFAULT_UNITS},
    )

    final_caption = f"{caption}\n\n{advice_text}" if advice_text else caption

    try:
        await message.answer_photo(
            photo=FSInputFile(str(icon_path)),
            caption=final_caption,
            parse_mode="HTML",
            reply_markup=reply_markup,
        )
    finally:
        if loader_message:
            with contextlib.suppress(Exception):
                await loader_message.delete()
