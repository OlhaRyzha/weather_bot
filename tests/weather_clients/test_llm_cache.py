import pytest
from bot.weather_clients.llm.cache import advice_cache_key, async_lru_cache


@pytest.mark.anyio("asyncio")
async def test_async_lru_cache_returns_cached_value():
    call_count = 0

    async def compute(value):
        nonlocal call_count
        call_count += 1
        return value * 2

    cached = async_lru_cache(maxsize=2, key_builder=lambda value: value)(compute)

    assert await cached(3) == 6
    assert await cached(3) == 6
    assert call_count == 1


@pytest.mark.anyio("asyncio")
async def test_async_lru_cache_discards_least_recently_used_entry():
    call_log: list[int] = []

    async def compute(value):
        call_log.append(value)
        return value * 10

    cached = async_lru_cache(maxsize=2, key_builder=lambda value: value)(compute)

    assert await cached(1) == 10
    assert await cached(2) == 20
    assert await cached(1) == 10
    assert await cached(3) == 30
    assert await cached(2) == 20
    assert call_log == [1, 2, 3, 2]


@pytest.mark.anyio("asyncio")
async def test_async_lru_cache_skips_when_key_builder_returns_none():
    call_count = 0

    async def compute(value):
        nonlocal call_count
        call_count += 1
        return value

    cached = async_lru_cache(maxsize=2, key_builder=lambda value: None)(compute)

    assert await cached("x") == "x"
    assert await cached("x") == "x"
    assert call_count == 2


def test_advice_cache_key_normalizes_inputs(fake_message_factory):
    message = fake_message_factory()
    message.from_user.id = 77

    key = advice_cache_key(
        message,
        city="  KYIV ",
        temp_c=5,
        description="  Foggy ",
        user_data={"b": 2, "a": 1},
    )

    assert key == (77, "kyiv", "foggy", 5, (("a", 1), ("b", 2)))


def test_advice_cache_key_returns_none_without_message():
    assert advice_cache_key(None, city="kyiv", temp_c=1, description="clear") is None
