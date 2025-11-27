import pytest
from bot.dialog_states import WeatherStates
from bot.routers.weather_router import city as city_router
from tests.fakes import FakeShortcuts

fake_shortcuts = FakeShortcuts()


@pytest.mark.anyio("asyncio")
async def test_ask_city_sets_state_and_prompts(
    monkeypatch, fake_message_factory, fake_state
):
    monkeypatch.setitem(city_router.MESSAGES, "enter_city", "Enter city:")
    message = fake_message_factory()

    await city_router.ask_city(message, fake_state)

    assert fake_state.state == WeatherStates.waiting_for_city
    assert message.answers[0]["text"] == "Enter city:"


@pytest.mark.anyio("asyncio")
async def test_city_weather_uses_shortcut_commands(
    monkeypatch, fake_message_factory, fake_state
):
    message = fake_message_factory(text="  HOME  ")

    async def fake_list(user_id):
        assert user_id == message.from_user.id
        return fake_shortcuts

    monkeypatch.setattr(city_router.shortcuts_storage, "list", fake_list)
    keyboard = {"commands": []}
    monkeypatch.setattr(
        city_router, "build_main_kb", lambda commands: keyboard | {"commands": commands}
    )

    captured = {}

    async def fake_get_weather(message_arg, **kwargs):
        captured["message"] = message_arg
        captured["kwargs"] = kwargs

    monkeypatch.setattr(city_router, "get_weather_by_city", fake_get_weather)

    await city_router.city_weather(message, fake_state)

    assert captured["message"] is not message
    assert captured["message"].text == "kyiv"
    assert captured["kwargs"]["display_name"] == "Home(Kyiv)"
    assert captured["kwargs"]["reply_markup"]["commands"] == ["home", "work"]
    assert ("clear", None) in fake_state.log


@pytest.mark.anyio("asyncio")
async def test_city_weather_forwards_message_when_no_shortcut(
    monkeypatch, fake_message_factory, fake_state
):
    message = fake_message_factory(text="warsaw")

    async def fake_list(user_id):
        return []

    monkeypatch.setattr(city_router.shortcuts_storage, "list", fake_list)
    monkeypatch.setattr(
        city_router, "build_main_kb", lambda commands: {"commands": commands}
    )

    captured = {}

    async def fake_get_weather(message_arg, **kwargs):
        captured["message"] = message_arg
        captured["kwargs"] = kwargs

    monkeypatch.setattr(city_router, "get_weather_by_city", fake_get_weather)

    await city_router.city_weather(message, fake_state)

    assert captured["message"] is message
    assert captured["kwargs"]["reply_markup"]["commands"] == []
    assert ("clear", None) in fake_state.log
