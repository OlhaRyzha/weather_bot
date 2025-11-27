from typing import cast
import pytest
from bot.dialog_states import WeatherStates
from bot.routers.weather_router import shortcuts as shortcuts_router
from bot.reply_keyboards.main_menu_keyboard import MAIN_BTN_LOCATION


@pytest.mark.anyio("asyncio")
async def test_ask_shortcut_command_sets_state(
    monkeypatch, fake_message_factory, fake_state
):
    message = fake_message_factory()

    await shortcuts_router.ask_shortcut_command(message, fake_state)

    assert fake_state.state == WeatherStates.waiting_for_shortcut_command
    assert message.answers[0]["text"] == shortcuts_router.MESSAGES["shortcut_command"]
    assert message.answers[0]["parse_mode"] == "HTML"


@pytest.mark.anyio("asyncio")
async def test_process_shortcut_command_accepts_new_command(
    monkeypatch, fake_message_factory, fake_state
):
    message = fake_message_factory(text="Home")

    async def fake_list(user_id):
        return []

    monkeypatch.setattr(shortcuts_router.shortcuts_storage, "list", fake_list)

    await shortcuts_router.process_shortcut_command(message, fake_state)

    assert fake_state.state == WeatherStates.waiting_for_shortcut_city
    assert fake_state.data["shortcut_command"] == "home"
    assert "home" in message.answers[0]["text"]


@pytest.mark.anyio("asyncio")
async def test_process_shortcut_command_rejects_empty(
    monkeypatch, fake_message_factory, fake_state
):
    message = fake_message_factory(text="   ")
    await shortcuts_router.process_shortcut_command(message, fake_state)
    assert message.answers[0]["text"].startswith("<code>Command</code>")
    assert fake_state.state is None


@pytest.mark.anyio("asyncio")
async def test_process_shortcut_command_rejects_spaces(
    monkeypatch, fake_message_factory, fake_state
):
    message = fake_message_factory(text="home office")
    await shortcuts_router.process_shortcut_command(message, fake_state)
    assert shortcuts_router.MESSAGES["space_error"] in message.answers[0]["text"]


@pytest.mark.anyio("asyncio")
async def test_process_shortcut_command_detects_duplicates(
    monkeypatch, fake_message_factory, fake_state
):
    message = fake_message_factory(text="home")

    async def fake_list(user_id):
        return [("home", "kyiv")]

    monkeypatch.setattr(shortcuts_router.shortcuts_storage, "list", fake_list)

    await shortcuts_router.process_shortcut_command(message, fake_state)
    assert "already exists" in message.answers[0]["text"]


@pytest.mark.anyio("asyncio")
async def test_add_shortcut_city_saves_and_updates_keyboard(
    monkeypatch, fake_message_factory, fake_state
):
    message = fake_message_factory(text="Kyiv")
    fake_state.data = {"shortcut_command": "home"}

    shortcuts: list[tuple[str, str]] = []

    async def fake_add(user_id, command, city):
        shortcuts.append((command, city))
        return list(shortcuts)

    async def fake_list(user_id):
        return list(shortcuts)

    monkeypatch.setattr(shortcuts_router.shortcuts_storage, "add", fake_add)
    monkeypatch.setattr(shortcuts_router.shortcuts_storage, "list", fake_list)
    monkeypatch.setattr(
        shortcuts_router, "build_main_kb", lambda commands: {"commands": commands}
    )

    await shortcuts_router.add_shortcut_city(message, fake_state)

    assert shortcuts == [("home", "kyiv")]
    assert message.answers[0]["reply_markup"]["commands"] == ["home"]
    assert fake_state.state is None
    assert fake_state.data == {}


@pytest.mark.anyio("asyncio")
async def test_add_shortcut_city_requires_city(
    monkeypatch, fake_message_factory, fake_state
):
    message = fake_message_factory(text="   ")
    await shortcuts_router.add_shortcut_city(message, fake_state)
    assert "City" in message.answers[0]["text"]


@pytest.mark.anyio("asyncio")
async def test_add_shortcut_city_handles_missing_command(
    monkeypatch, fake_message_factory, fake_state
):
    message = fake_message_factory(text="Kyiv")
    fake_state.data = {}

    await shortcuts_router.add_shortcut_city(message, fake_state)

    assert message.answers[-1]["text"] == shortcuts_router.MESSAGES["smth_wrong"]


@pytest.mark.anyio("asyncio")
async def test_show_shortcuts_lists_existing(
    monkeypatch, fake_message_factory, fake_state
):
    message = fake_message_factory()

    async def fake_list(user_id):
        return [("home", "kyiv"), ("work", "lviv")]

    monkeypatch.setattr(shortcuts_router.shortcuts_storage, "list", fake_list)
    monkeypatch.setattr(
        shortcuts_router, "build_main_kb", lambda commands: {"commands": commands}
    )

    await shortcuts_router.show_shortcuts(message, fake_state)

    assert "home" in message.answers[0]["text"]
    assert message.answers[0]["reply_markup"]["commands"] == ["home", "work"]


@pytest.mark.anyio("asyncio")
async def test_show_shortcuts_informs_when_empty(
    monkeypatch, fake_message_factory, fake_state
):
    message = fake_message_factory()

    async def fake_list(user_id):
        return []

    monkeypatch.setattr(shortcuts_router.shortcuts_storage, "list", fake_list)
    monkeypatch.setattr(
        shortcuts_router, "build_main_kb", lambda commands: {"commands": commands}
    )

    await shortcuts_router.show_shortcuts(message, fake_state)

    assert (
        message.answers[0]["text"] == shortcuts_router.MESSAGES["dont_have_shortcuts"]
    )


@pytest.mark.anyio("asyncio")
async def test_handle_shortcut_or_fallback_matches_command(
    monkeypatch, fake_message_factory, fake_state
):
    message = fake_message_factory(text="Home")

    async def fake_list(user_id):
        return [("home", "kyiv")]

    monkeypatch.setattr(shortcuts_router.shortcuts_storage, "list", fake_list)
    monkeypatch.setattr(
        shortcuts_router, "build_main_kb", lambda commands: {"commands": commands}
    )

    captured = {}

    async def fake_get_weather(message_arg, **kwargs):
        captured["message"] = message_arg
        captured["kwargs"] = kwargs

    monkeypatch.setattr(shortcuts_router, "get_weather_by_city", fake_get_weather)

    await shortcuts_router.handle_shortcut_or_fallback(message, fake_state)

    assert captured["message"] is not message
    assert captured["message"].text == "kyiv"
    assert captured["kwargs"]["display_name"] == "Home(Kyiv)"
    assert captured["kwargs"]["reply_markup"]["commands"] == ["home"]


@pytest.mark.anyio("asyncio")
async def test_handle_shortcut_or_fallback_forwards_unknown_text(
    monkeypatch, fake_message_factory, fake_state
):
    message = fake_message_factory(text=cast(str, "Unknown"))

    async def fake_list(user_id):
        return []

    monkeypatch.setattr(shortcuts_router.shortcuts_storage, "list", fake_list)
    monkeypatch.setattr(
        shortcuts_router, "build_main_kb", lambda commands: {"commands": commands}
    )

    captured = {}

    async def fake_get_weather(message_arg, **kwargs):
        captured["message"] = message_arg
        captured["kwargs"] = kwargs

    monkeypatch.setattr(shortcuts_router, "get_weather_by_city", fake_get_weather)

    await shortcuts_router.handle_shortcut_or_fallback(message, fake_state)

    assert captured["message"] is message
    assert captured["kwargs"]["reply_markup"]["commands"] == []


@pytest.mark.anyio("asyncio")
async def test_handle_shortcut_or_fallback_ignores_location_button(
    monkeypatch, fake_message_factory, fake_state
):
    message = fake_message_factory(text=MAIN_BTN_LOCATION)

    async def fake_list(user_id):
        return []

    monkeypatch.setattr(shortcuts_router.shortcuts_storage, "list", fake_list)

    async def fake_get_weather(*args, **kwargs):
        raise AssertionError(
            "should not call weather service when pressing location button"
        )

    monkeypatch.setattr(shortcuts_router, "get_weather_by_city", fake_get_weather)

    await shortcuts_router.handle_shortcut_or_fallback(message, fake_state)

    assert fake_state.log == []
