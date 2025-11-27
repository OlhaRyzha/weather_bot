import pytest
from bot.routers.weather_router import start as start_router
from tests.fakes import FakeShortcuts

fake_shortcuts = FakeShortcuts()


@pytest.mark.anyio("asyncio")
async def test_on_start_lists_shortcuts_and_greets(
    monkeypatch, fake_message_factory, fake_state
):
    message = fake_message_factory()

    async def fake_list(user_id):
        assert user_id == message.from_user.id
        return fake_shortcuts

    monkeypatch.setattr(start_router.shortcuts_storage, "list", fake_list)
    monkeypatch.setattr(
        start_router,
        "get_greeting_message",
        lambda user: f"Hi, {user.id}",
    )
    keyboard = {"from": "builder"}
    monkeypatch.setattr(
        start_router,
        "build_main_kb",
        lambda commands: keyboard | {"commands": commands},
    )

    await start_router.on_start(message, fake_state)

    assert ("clear", None) in fake_state.log
    assert message.answers[0]["text"] == f"Hi, {message.from_user.id}"
    assert message.answers[0]["reply_markup"]["commands"] == ["home", "work"]
