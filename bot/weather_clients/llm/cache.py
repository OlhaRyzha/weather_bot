from collections import OrderedDict
from functools import wraps
from typing import (
    Awaitable,
    Callable,
    Hashable,
    Mapping,
    Optional,
    ParamSpec,
    TypeVar,
)
from bot.helpers import normalize_text
from aiogram.types import Message

P = ParamSpec("P")
T = TypeVar("T")


def async_lru_cache(
    maxsize: int,
    key_builder: Callable[..., Optional[Hashable]],
):
    def decorator(func: Callable[P, Awaitable[T]]):
        cache: OrderedDict[Hashable, T] = OrderedDict()

        @wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            cache_key = key_builder(*args, **kwargs)
            if cache_key is None:
                return await func(*args, **kwargs)

            if cache_key in cache:
                value = cache.pop(cache_key)
                cache[cache_key] = value
                return value

            value = await func(*args, **kwargs)
            cache[cache_key] = value
            if len(cache) > maxsize:
                cache.popitem(last=False)
            return value

        return wrapper

    return decorator


def advice_cache_key(
    message: Message | None = None,
    *,
    city: str = "",
    temp_c: int = 0,
    description: str = "",
    user_data: Mapping[str, object] | None = None,
):
    if message is None:
        return None

    normalized_city = normalize_text(city)
    normalized_description = normalize_text(description)
    user_data_key = tuple(sorted(user_data.items())) if user_data is not None else None
    user_id = message.from_user.id if message.from_user else None

    return (
        user_id,
        normalized_city,
        normalized_description,
        temp_c,
        user_data_key,
    )
