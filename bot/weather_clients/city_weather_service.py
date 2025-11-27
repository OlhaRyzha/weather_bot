from aiogram.types import Message, ReplyKeyboardMarkup
from bot.helpers import normalize_text
from config.settings import MESSAGES
from .base_weather_service import send_weather_response


async def get_weather_by_city(
    message: Message,
    reply_markup: ReplyKeyboardMarkup | None = None,
    *,
    display_name: str | None = None,
):
    """Fetch weather data for a city name provided in a text message."""
    city = normalize_text(message.text or "")
    if not city:
        await message.answer(MESSAGES["provide_valid_city"], reply_markup=reply_markup)
        return

    await send_weather_response(
        message,
        query_params={"q": city},
        fallback_city=city,
        display_name=display_name,
        reply_markup=reply_markup,
    )
