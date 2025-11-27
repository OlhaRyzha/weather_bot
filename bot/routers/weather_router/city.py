from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from bot.dialog_states import WeatherStates
from bot.helpers import normalize_text
from bot.reply_keyboards.main_menu_keyboard import (
    MAIN_BTN_CITY,
    build_main_kb,
)
from bot.repositories import shortcuts_storage
from bot.weather_clients.city_weather_service import get_weather_by_city
from config.settings import MESSAGES

router = Router()


@router.message(F.text == MAIN_BTN_CITY)
async def ask_city(message: Message, state: FSMContext):
    await state.set_state(WeatherStates.waiting_for_city)
    await message.answer(MESSAGES["enter_city"])


@router.message(WeatherStates.waiting_for_city, F.text)
async def city_weather(message: Message, state: FSMContext):
    user_id = message.from_user.id if message.from_user else 0
    text_raw = message.text or ""
    text = normalize_text(text_raw)
    shortcuts = await shortcuts_storage.list(user_id)
    commands = [cmd for cmd, _ in shortcuts]
    command_to_city = {cmd: city for cmd, city in shortcuts}
    reply_markup = build_main_kb(commands)

    if text in command_to_city:
        city = command_to_city[text]
        command_display = text.capitalize()
        city_display = city.title()
        display_name = f"{command_display}({city_display})"

        fake_message = message.model_copy(update={"text": city})
        await get_weather_by_city(
            fake_message,
            reply_markup=reply_markup,
            display_name=display_name,
        )
    else:
        await get_weather_by_city(message, reply_markup=reply_markup)

    await state.clear()
