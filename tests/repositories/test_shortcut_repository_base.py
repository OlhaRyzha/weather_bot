import pytest
from bot.repositories.shortcut_repository import base as base_module


class IncompleteRepo(base_module.ShortcutRepository):
    async def list(self, user_id: int):
        return await base_module.ShortcutRepository.list(self, user_id)  # type: ignore[misc]

    async def add(self, user_id: int, command: str, city: str):
        return await base_module.ShortcutRepository.add(self, user_id, command, city)  # type: ignore[misc]


@pytest.mark.anyio("asyncio")
async def test_base_methods_raise_not_implemented():
    repo = IncompleteRepo()
    with pytest.raises(NotImplementedError):
        await repo.list(1)
    with pytest.raises(NotImplementedError):
        await repo.add(1, "home", "kyiv")
