
from bot.helpers.text_formatters import (
    format_temperature_message,
    get_full_name,
    get_greeting_message,
    normalize_text,
)


def test_normalize_text_trims_and_lowercases():
    assert normalize_text("  Kyiv  ") == "kyiv"
    assert normalize_text(None) == ""


def test_format_temperature_message_capitalizes_city():
    message = format_temperature_message("kyiv", 12, "clear sky")
    assert "<b>Kyiv</b>" in message
    assert "Temperature: <b>12°C</b>" in message
    assert "Clear sky" in message


def test_get_full_name_and_greeting(fake_user):
    assert get_full_name(fake_user) == fake_user.full_name
    assert get_full_name(None) == ""

    greeting = get_greeting_message(fake_user)
    assert fake_user.full_name in greeting
    assert greeting.startswith("Hello")

    assert get_greeting_message(None).startswith("Hello!")
