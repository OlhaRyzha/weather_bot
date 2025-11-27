from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from bot.helpers.text_formatters import get_greeting_message
from bot.reply_keyboards.main_menu_keyboard import build_main_kb
from bot.repositories import shortcuts_storage

router = Router()


@router.message(CommandStart())
async def on_start(message: Message, state: FSMContext):
    await state.clear()
    user = message.from_user
    user_id = user.id if user else 0

    shortcuts = await shortcuts_storage.list(user_id)
    commands = [cmd for cmd, _ in shortcuts]
    message_text = get_greeting_message(user)

    await message.answer(
        message_text,
        reply_markup=build_main_kb(commands),
    )
