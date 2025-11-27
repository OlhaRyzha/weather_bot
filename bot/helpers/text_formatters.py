from aiogram.types import User


def normalize_text(text: str | None = ""):
    return text.lower().strip() if text else ""


def format_temperature_message(city: str, temp: int, description: str):
    prettified_city = city if any(ch.isupper() for ch in city) else city.title()
    return (
        f"<b>{prettified_city}</b>\n"
        f"Temperature: <b>{temp}°C</b>\n"
        f"{description.capitalize()}"
    )


def get_full_name(user: User | None):
    full_name = user.full_name if user else ""

    return full_name


def get_greeting_message(user: User | None):
    full_name = get_full_name(user)

    return (f"Hello, {full_name}!" if user else "Hello!") + "\nChoose an action:"
