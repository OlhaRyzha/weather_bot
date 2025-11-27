from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from bot.reply_keyboards.main_menu_keyboard import (
    MAIN_BTN_LOCATION,
    build_main_kb,
)
from bot.repositories import shortcuts_storage
from bot.weather_clients.location_weather_service import get_weather_by_coords

router = Router()


async def _process_location_request(message: Message, state: FSMContext):
    user_id = message.from_user.id if message.from_user else 0
    shortcuts = await shortcuts_storage.list(user_id)
    commands = [cmd for cmd, _ in shortcuts]
    reply_markup = build_main_kb(commands)

    await get_weather_by_coords(message, reply_markup=reply_markup)
    await state.clear()


@router.message(StateFilter("*"), F.location)
async def weather_by_location(message: Message, state: FSMContext):
    await _process_location_request(message, state)


@router.message(StateFilter("*"), F.text == MAIN_BTN_LOCATION)
async def weather_by_location_fallback(message: Message, state: FSMContext):
    await _process_location_request(message, state)
