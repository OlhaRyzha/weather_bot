from types import SimpleNamespace
from typing import cast
import pytest
from bot.lifecycle import shutdown as shutdown_module
from bot.lifecycle import startup as startup_module


@pytest.mark.anyio("asyncio")
async def test_on_startup_skips_when_mysql_disabled(monkeypatch):
    monkeypatch.setattr(startup_module, "MYSQL", SimpleNamespace(enabled=False))

    async def fail_if_called():
        raise AssertionError("init_mysql_pool should not run")

    monkeypatch.setattr(startup_module, "init_mysql_pool", fail_if_called)

    logged = []
    monkeypatch.setattr(startup_module.logging, "info", logged.append)

    fake_bot = cast(startup_module.Bot, object())

    await startup_module.on_startup(bot=fake_bot)

    assert logged == [startup_module.MESSAGES["msql_disabled"]]


@pytest.mark.anyio("asyncio")
async def test_on_startup_initializes_mysql(monkeypatch):
    monkeypatch.setattr(startup_module, "MYSQL", SimpleNamespace(enabled=True))

    async def fake_init():
        return "pool-object"

    monkeypatch.setattr(startup_module, "init_mysql_pool", fake_init)

    captured = {}

    class DummyRepo:
        def __init__(self, pool):
            captured["pool"] = pool

        async def ensure_schema(self):
            captured["schema"] = True

    monkeypatch.setattr(startup_module, "MySQLShortcutRepository", DummyRepo)

    def fake_set_backend(repo):
        captured["backend"] = repo

    monkeypatch.setattr(
        startup_module.shortcuts_storage, "set_backend", fake_set_backend
    )

    logs = []
    monkeypatch.setattr(startup_module.logging, "info", logs.append)

    fake_bot = cast(startup_module.Bot, object())

    await startup_module.on_startup(bot=fake_bot)

    assert captured["pool"] == "pool-object"
    assert captured["backend"] is not None
    assert captured["schema"] is True
    assert logs[-1] == startup_module.MESSAGES["msql_ready"]


@pytest.mark.anyio("asyncio")
async def test_on_shutdown_closes_pool(monkeypatch):
    called = {"closed": False}

    async def fake_close():
        called["closed"] = True

    monkeypatch.setattr(shutdown_module, "close_mysql_pool", fake_close)

    fake_bot = cast(shutdown_module.Bot, object())

    await shutdown_module.on_shutdown(bot=fake_bot)

    assert called["closed"] is True
