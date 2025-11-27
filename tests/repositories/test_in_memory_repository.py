import pytest
from tests.fakes import HOME_KYIV, HOME_ODESA, HOME_WARSAW, FakeShortcuts


fake_shortcuts = FakeShortcuts()


@pytest.mark.anyio("asyncio")
async def test_list_returns_new_copy(in_memory_repo):
    result = await in_memory_repo.list(user_id=1)
    assert result == []

    result.append(("temp", "city"))
    fresh = await in_memory_repo.list(user_id=1)
    assert fresh == []


@pytest.mark.anyio("asyncio")
async def test_add_appends_and_updates(in_memory_repo):
    await in_memory_repo.add(1, *fake_shortcuts.home)
    await in_memory_repo.add(1, *fake_shortcuts.work)

    shortcuts = await in_memory_repo.list(1)
    assert shortcuts == fake_shortcuts.shortcuts

    await in_memory_repo.add(1, *HOME_ODESA)

    updated = await in_memory_repo.list(1)
    assert updated[0] == HOME_ODESA


@pytest.mark.anyio("asyncio")
async def test_data_is_isolated_per_user(in_memory_repo):
    await in_memory_repo.add(1, *HOME_KYIV)
    await in_memory_repo.add(2, *HOME_WARSAW)

    shortcuts_user1 = await in_memory_repo.list(1)
    shortcuts_user2 = await in_memory_repo.list(2)

    assert shortcuts_user1 == [HOME_KYIV]
    assert shortcuts_user2 == [HOME_WARSAW]
