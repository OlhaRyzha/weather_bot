from aiogram.types import Message, ReplyKeyboardMarkup
from config.settings import MESSAGES
from .base_weather_service import send_weather_response


async def get_weather_by_coords(
    message: Message, reply_markup: ReplyKeyboardMarkup | None = None
):
    """Fetch weather data by coordinates from a location message."""
    if not message.location:
        await message.answer(
            MESSAGES["share_location"],
            reply_markup=reply_markup,
        )
        return

    lat, lon = message.location.latitude, message.location.longitude
    await send_weather_response(
        message,
        query_params={"lat": lat, "lon": lon},
        reply_markup=reply_markup,
    )
