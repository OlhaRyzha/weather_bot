import pytest
from bot.weather_clients.city_weather_service import get_weather_by_city


@pytest.mark.anyio("asyncio")
async def test_get_weather_by_city_requires_text(fake_message_factory):
    message = fake_message_factory(text="   ")
    await get_weather_by_city(message)

    assert len(message.answers) == 1
    assert message.answers[0]["text"] == "Please provide a valid city name."


@pytest.mark.anyio("asyncio")
async def test_get_weather_by_city_delegates_to_base(monkeypatch, fake_message_factory):
    captured = {}

    async def fake_send(message, **kwargs):
        captured["message"] = message
        captured["kwargs"] = kwargs

    monkeypatch.setattr(
        "bot.weather_clients.city_weather_service.send_weather_response",
        fake_send,
    )

    message = fake_message_factory(text="  lviv  ")
    await get_weather_by_city(
        message,
        reply_markup="kb",
        display_name="Home city",
    )

    assert captured["message"] is message
    assert captured["kwargs"]["query_params"] == {"q": "lviv"}
    assert captured["kwargs"]["fallback_city"] == "lviv"
    assert captured["kwargs"]["display_name"] == "Home city"
    assert captured["kwargs"]["reply_markup"] == "kb"
