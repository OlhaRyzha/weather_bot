from asyncio import Lock
from typing import Optional, cast
from aiomysql import Pool, create_pool
from config.settings import MESSAGES, MYSQL


_pool: Optional[Pool] = None
_pool_lock = Lock()


async def init_mysql_pool() -> Pool:
    global _pool

    if not MYSQL.enabled:
        raise RuntimeError(MESSAGES["msql_disabled"])

    if _pool is not None:
        return _pool

    async with _pool_lock:
        if _pool is not None:
            return _pool

        pool = cast(
            Pool,
            await create_pool(
                host=MYSQL.host,
                port=MYSQL.port,
                user=MYSQL.user,
                password=MYSQL.password,
                db=MYSQL.database,
                autocommit=True,
                minsize=MYSQL.min_pool_size,
                maxsize=MYSQL.max_pool_size,
                connect_timeout=MYSQL.connect_timeout,
                charset="utf8mb4",
            ),
        )
        _pool = pool
        return _pool


def get_mysql_pool() -> Pool:
    if _pool is None:
        raise RuntimeError(MESSAGES["msql_pool_error"])
    return _pool


async def close_mysql_pool():
    global _pool
    if _pool is None:
        return
    _pool.close()
    await _pool.wait_closed()
    _pool = None
