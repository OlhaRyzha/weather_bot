from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

MAIN_BTN_CITY = "🗺️ Weather by city"
MAIN_BTN_LOCATION = "📍 Share location"
MAIN_BTN_ADD_SHORTCUT = "🖋 Add shortcut"
MAIN_BTN_SHOW_SHORTCUT = "🗂 Show all shortcuts"


def build_main_kb(shortcuts: list[str]) -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()

    kb.button(text=MAIN_BTN_CITY)
    kb.button(text=MAIN_BTN_LOCATION, request_location=True)
    kb.button(text=MAIN_BTN_ADD_SHORTCUT)
    kb.button(text=MAIN_BTN_SHOW_SHORTCUT)

    for command in shortcuts:
        kb.button(text=command.capitalize())

    if shortcuts:
        kb.adjust(2, 1, 3)
    else:
        kb.adjust(2, 1)

    return kb.as_markup(resize_keyboard=True, one_time_keyboard=False)
