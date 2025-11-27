import asyncio
from types import SimpleNamespace
import pytest
import bot.db.mysql as mysql_module


@pytest.fixture(autouse=True)
def reset_pool():
    mysql_module._pool = None
    yield
    mysql_module._pool = None


@pytest.mark.anyio("asyncio")
async def test_init_mysql_pool_requires_mysql(monkeypatch):
    monkeypatch.setattr(mysql_module, "MYSQL", SimpleNamespace(enabled=False))

    with pytest.raises(RuntimeError):
        await mysql_module.init_mysql_pool()


class DummyPool:
    def __init__(self):
        self.closed = False
        self.waited = False

    def close(self):
        self.closed = True

    async def wait_closed(self):
        self.waited = True


@pytest.mark.anyio("asyncio")
async def test_init_get_and_close_pool(monkeypatch):
    dummy = DummyPool()
    lock = asyncio.Lock()
    monkeypatch.setattr(mysql_module, "_pool_lock", lock)
    monkeypatch.setattr(
        mysql_module,
        "MYSQL",
        SimpleNamespace(
            enabled=True,
            host="db",
            port=3306,
            user="user",
            password="pw",
            database="weather",
            min_pool_size=1,
            max_pool_size=5,
            connect_timeout=3.5,
        ),
    )

    async def fake_create_pool(**kwargs):
        return dummy

    monkeypatch.setattr(mysql_module, "create_pool", fake_create_pool)

    pool = await mysql_module.init_mysql_pool()
    assert pool is dummy
    assert await mysql_module.init_mysql_pool() is dummy

    assert mysql_module.get_mysql_pool() is dummy

    await mysql_module.close_mysql_pool()
    assert dummy.closed is True
    assert dummy.waited is True

    with pytest.raises(RuntimeError):
        mysql_module.get_mysql_pool()
