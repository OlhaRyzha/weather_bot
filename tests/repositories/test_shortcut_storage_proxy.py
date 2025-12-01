import pytest
from typing import cast
from bot.repositories.shortcut_repository import ShortcutRepository
from bot.repositories.shortcut_repository.storage import ShortcutStorageProxy
from tests.fakes import HOME_KYIV, WORK_LVIV


class DummyRepo:
    def __init__(self):
        self.calls = []

    async def list(self, user_id: int):
        self.calls.append(("list", user_id))
        return [HOME_KYIV]

    async def add(self, user_id: int, command: str, city: str):
        self.calls.append(("add", user_id, command, city))
        return [HOME_KYIV, (command, city)]


@pytest.mark.anyio("asyncio")
async def test_storage_proxy_uses_backend():
    backend = DummyRepo()
    proxy = ShortcutStorageProxy(cast(ShortcutRepository, backend))

    assert await proxy.list(1) == [HOME_KYIV]
    result = await proxy.add(1, *WORK_LVIV)
    assert result[-1] == WORK_LVIV

    assert ("list", 1) in backend.calls
    assert ("add", 1, *WORK_LVIV) in backend.calls


@pytest.mark.anyio("asyncio")
async def test_storage_proxy_can_switch_backend():
    proxy = ShortcutStorageProxy()
    new_backend = cast(ShortcutRepository, DummyRepo())
    proxy.set_backend(new_backend)
    assert await proxy.list(1) == [HOME_KYIV]
