from typing import cast
import pytest
from bot.repositories.shortcut_repository.mysql import MySQLShortcutRepository, Pool
from tests.fakes import GYM_WARSAW, FakeShortcuts

fake_shortcuts = FakeShortcuts().shortcuts


class _CursorContext:
    def __init__(self, cursor):
        self._cursor = cursor

    async def __aenter__(self):
        return self._cursor

    async def __aexit__(self, exc_type, exc, tb):
        return False


class _ConnContext:
    def __init__(self, connection):
        self._connection = connection

    async def __aenter__(self):
        return self._connection

    async def __aexit__(self, exc_type, exc, tb):
        return False


class FakeCursor:
    def __init__(self, rows=None):
        self.rows = rows or []
        self.queries = []

    async def execute(self, sql, params=None):
        self.queries.append((sql, params))

    async def fetchall(self):
        return self.rows


class FakeConnection:
    def __init__(self, cursor):
        self._cursor = cursor

    def cursor(self):
        return _CursorContext(self._cursor)


class FakePool:
    def __init__(self, cursors):
        self._cursors = iter(cursors)

    def acquire(self):
        cursor = next(self._cursors)
        return _ConnContext(FakeConnection(cursor))


@pytest.mark.anyio("asyncio")
async def test_mysql_repository_operations():
    schema_cursor = FakeCursor()
    list_cursor = FakeCursor(rows=fake_shortcuts)
    add_cursor = FakeCursor()
    list_after_add = FakeCursor(rows=[*fake_shortcuts, GYM_WARSAW])

    pool = FakePool([schema_cursor, list_cursor, add_cursor, list_after_add])
    repo = MySQLShortcutRepository(cast(Pool, pool))

    await repo.ensure_schema()
    assert schema_cursor.queries

    listed = await repo.list(1)
    assert listed == fake_shortcuts

    result = await repo.add(1, *GYM_WARSAW)
    assert result[-1] == GYM_WARSAW
