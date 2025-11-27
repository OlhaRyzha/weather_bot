import asyncio
import inspect
import sys
from types import ModuleType
import pytest
from bot.repositories.shortcut_repository import InMemoryShortcutRepository
from tests.fakes import FakeFSMContext, FakeLocation, FakeMessage, FakeUser


@pytest.hookimpl(tryfirst=True)
def pytest_pyfunc_call(pyfuncitem):
    """Minimal async test runner fallback when pytest-anyio is unavailable."""
    test_func = pyfuncitem.obj
    if inspect.iscoroutinefunction(test_func):
        argnames = pyfuncitem._fixtureinfo.argnames if pyfuncitem._fixtureinfo else ()
        kwargs = {
            name: pyfuncitem.funcargs[name]
            for name in argnames or ()
            if name in pyfuncitem.funcargs
        }
        kwargs.pop("anyio_backend", None)
        loop = asyncio.new_event_loop()
        try:
            loop.run_until_complete(test_func(**kwargs))
        finally:
            loop.close()
        return True
    return None


if "aiomysql" not in sys.modules:
    aiomysql_stub = ModuleType("aiomysql")

    class _DummyPool:
        def __init__(self):
            self.closed = False

        def close(self):
            self.closed = True

        async def wait_closed(self):
            return

    setattr(aiomysql_stub, "Pool", _DummyPool)

    async def _create_pool(*args, **kwargs):
        return _DummyPool()

    setattr(aiomysql_stub, "create_pool", _create_pool)
    sys.modules["aiomysql"] = aiomysql_stub


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture
def fake_user() -> FakeUser:
    return FakeUser(id=42, first_name="Jane", last_name="Doe")


@pytest.fixture
def fake_message_factory(fake_user):
    def _factory(*, text: str | None = "", location: FakeLocation | None = None):
        return FakeMessage(text=text, user=fake_user, location=location)

    return _factory


@pytest.fixture
def in_memory_repo():
    return InMemoryShortcutRepository()


@pytest.fixture
def fake_state():
    return FakeFSMContext()
