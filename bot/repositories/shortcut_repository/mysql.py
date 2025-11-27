from dataclasses import dataclass
from aiomysql import Pool
from .base import ShortcutRepository
from .constants import (
    CREATE_SHORTCUTS_TABLE_SQL,
    SELECT_SHORTCUTS_SQL,
    UPSERT_SHORTCUTS_SQL,
)


@dataclass
class MySQLShortcutRepository(ShortcutRepository):
    pool: Pool

    async def ensure_schema(self):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(CREATE_SHORTCUTS_TABLE_SQL)

    async def list(self, user_id: int):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(SELECT_SHORTCUTS_SQL, (user_id,))
                rows = await cur.fetchall()

        return [(row[0], row[1]) for row in rows]

    async def add(self, user_id: int, command: str, city: str):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(UPSERT_SHORTCUTS_SQL, (user_id, command, city))

        return await self.list(user_id)
