import pytest
from bot.routers.weather_router import location as location_router
from tests.fakes import HOME_KYIV, FakeLocation


@pytest.mark.anyio("asyncio")
async def test_process_location_request_builds_keyboard(
    monkeypatch, fake_message_factory, fake_state
):
    message = fake_message_factory(
        location=FakeLocation(latitude=50.45, longitude=30.52)
    )

    async def fake_list(user_id):
        assert user_id == message.from_user.id
        return [HOME_KYIV]

    monkeypatch.setattr(location_router.shortcuts_storage, "list", fake_list)
    keyboard = {"commands": []}
    monkeypatch.setattr(
        location_router,
        "build_main_kb",
        lambda commands: keyboard | {"commands": commands},
    )

    captured = {}

    async def fake_get_weather(message_arg, *, reply_markup):
        captured["message"] = message_arg
        captured["reply_markup"] = reply_markup

    monkeypatch.setattr(location_router, "get_weather_by_coords", fake_get_weather)

    await location_router.weather_by_location(message, fake_state)

    assert captured["message"] is message
    assert captured["reply_markup"]["commands"] == ["home"]
    assert ("clear", None) in fake_state.log


@pytest.mark.anyio("asyncio")
async def test_weather_by_location_fallback_invokes_processor(
    monkeypatch, fake_message_factory, fake_state
):
    called = {"count": 0}

    async def fake_process(message, state):
        called["count"] += 1

    monkeypatch.setattr(location_router, "_process_location_request", fake_process)

    await location_router.weather_by_location_fallback(
        fake_message_factory(), fake_state
    )

    assert called["count"] == 1
