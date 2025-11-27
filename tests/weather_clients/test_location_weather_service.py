import pytest
from bot.weather_clients.location_weather_service import get_weather_by_coords
from tests.fakes import FakeLocation


@pytest.mark.anyio("asyncio")
async def test_get_weather_by_coords_requires_location(fake_message_factory):
    message = fake_message_factory(text="city")
    await get_weather_by_coords(message, reply_markup="kb")

    assert len(message.answers) == 1
    assert "Please share your location" in message.answers[0]["text"]
    assert message.answers[0]["reply_markup"] == "kb"


@pytest.mark.anyio("asyncio")
async def test_get_weather_by_coords_delegates_to_base(
    monkeypatch, fake_message_factory
):
    captured = {}

    async def fake_send(message, **kwargs):
        captured["message"] = message
        captured["kwargs"] = kwargs

    monkeypatch.setattr(
        "bot.weather_clients.location_weather_service.send_weather_response",
        fake_send,
    )

    message = fake_message_factory(
        location=FakeLocation(latitude=50.45, longitude=30.52)
    )
    await get_weather_by_coords(message, reply_markup="kb")

    assert captured["message"] is message
    assert captured["kwargs"]["query_params"] == {"lat": 50.45, "lon": 30.52}
    assert captured["kwargs"]["reply_markup"] == "kb"
