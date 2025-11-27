from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from bot.dialog_states import WeatherStates
from bot.helpers import normalize_text
from bot.reply_keyboards.main_menu_keyboard import (
    MAIN_BTN_ADD_SHORTCUT,
    MAIN_BTN_LOCATION,
    MAIN_BTN_SHOW_SHORTCUT,
    build_main_kb,
)
from bot.repositories import shortcuts_storage
from bot.weather_clients.city_weather_service import get_weather_by_city
from config.settings import MESSAGES
from aiogram.types import Message


router = Router()


@router.message(F.text == MAIN_BTN_ADD_SHORTCUT)
async def ask_shortcut_command(message: Message, state: FSMContext):
    await state.set_state(WeatherStates.waiting_for_shortcut_command)
    await message.answer(
        MESSAGES["shortcut_command"],
        parse_mode="HTML",
    )


@router.message(WeatherStates.waiting_for_shortcut_command, F.text)
async def process_shortcut_command(message: Message, state: FSMContext):
    user_id = message.from_user.id if message.from_user else 0
    raw_command = message.text or ""
    command = normalize_text(raw_command)

    if not command:
        await message.answer(MESSAGES["empty_error"].format(entity="Command"))
        return

    if " " in command:
        await message.answer(MESSAGES["space_error"], parse_mode="HTML")
        return

    shortcuts = await shortcuts_storage.list(user_id)
    existing_commands = {cmd for cmd, _ in shortcuts}

    if command in existing_commands:
        await message.answer(
            MESSAGES["already_exists"].format(command=command),
            parse_mode="HTML",
        )
        return

    await state.update_data(shortcut_command=command)
    await state.set_state(WeatherStates.waiting_for_shortcut_city)
    await message.answer(
        MESSAGES["entered_city"].format(command=command),
        parse_mode="HTML",
    )


@router.message(WeatherStates.waiting_for_shortcut_city, F.text)
async def add_shortcut_city(message: Message, state: FSMContext):
    user_id = message.from_user.id if message.from_user else 0
    city = normalize_text(message.text or "")

    if not city:
        await message.answer(MESSAGES["empty_error"].format(entity="City"))
        return

    data = await state.get_data()
    command = data.get("shortcut_command")
    if not command:
        await state.clear()
        await message.answer(MESSAGES["smth_wrong"])
        return

    await shortcuts_storage.add(user_id, command, city)
    await state.clear()

    shortcuts = await shortcuts_storage.list(user_id)
    commands = [cmd for cmd, _ in shortcuts]

    await message.answer(
        MESSAGES["shortcut_added"].format(command=command, city=city),
        parse_mode="HTML",
        reply_markup=build_main_kb(commands),
    )


@router.message(F.text == MAIN_BTN_SHOW_SHORTCUT)
async def show_shortcuts(message: Message, state: FSMContext):
    user_id = message.from_user.id if message.from_user else 0
    shortcuts = await shortcuts_storage.list(user_id)

    if not shortcuts:
        await message.answer(
            MESSAGES["dont_have_shortcuts"],
            reply_markup=build_main_kb([]),
        )
        return

    lines = [f"🔷 <code>{cmd}</code> → <b>{city}</b>" for cmd, city in shortcuts]
    text = "Your shortcuts:\n\n" + "\n".join(lines)

    commands = [cmd for cmd, _ in shortcuts]

    await message.answer(
        text,
        parse_mode="HTML",
        reply_markup=build_main_kb(commands),
    )


@router.message(F.text)
async def handle_shortcut_or_fallback(message: Message, state: FSMContext):
    user_id = message.from_user.id if message.from_user else 0
    text_raw = message.text or ""
    text = normalize_text(text_raw)

    if text_raw == MAIN_BTN_LOCATION:
        return

    shortcuts = await shortcuts_storage.list(user_id)
    commands = [cmd for cmd, _ in shortcuts]
    command_to_city = {cmd: city for cmd, city in shortcuts}

    if text in command_to_city:
        city = command_to_city[text]
        command_display = text.capitalize()
        city_display = city.title()
        display_name = f"{command_display}({city_display})"

        fake_message = message.model_copy(update={"text": city})

        await get_weather_by_city(
            fake_message,
            reply_markup=build_main_kb(commands),
            display_name=display_name,
        )
        return

    await get_weather_by_city(
        message,
        reply_markup=build_main_kb(commands),
    )
