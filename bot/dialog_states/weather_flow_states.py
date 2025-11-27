from aiogram.fsm.state import StatesGroup, State


class WeatherStates(StatesGroup):
    waiting_for_city = State()
    waiting_for_shortcut_command = State()
    waiting_for_shortcut_city = State()
