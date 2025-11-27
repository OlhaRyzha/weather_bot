import os
from typing import Final, TypeVar, overload

TRUTHY_VALUES: Final[set[str]] = {"1", "true", "t", "yes", "y"}


class _MissingType:
    __slots__ = ()


_MISSING: Final = _MissingType()
_T = TypeVar("_T")


def is_truthy(raw: str) -> bool:
    return raw.lower() in TRUTHY_VALUES


def bool_env(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return is_truthy(raw)


@overload
def _resolve_env_value(name: str) -> str: ...


@overload
def _resolve_env_value(name: str, default: _T) -> str | _T: ...


def _resolve_env_value(name: str, default: _MissingType | _T = _MISSING) -> str | _T:
    value = os.getenv(name)
    if value is None:
        if isinstance(default, _MissingType):
            raise RuntimeError(f"Environment variable {name} is not set")
        return default
    return value


def str_env(name: str, default: str | None | _MissingType = _MISSING) -> str:
    if isinstance(default, _MissingType):
        value = _resolve_env_value(name)
    else:
        value = _resolve_env_value(name, default)
    if value is None:
        return ""
    return str(value)


@overload
def int_env(name: str) -> int: ...


@overload
def int_env(name: str, default: int | str) -> int: ...


def int_env(name: str, default: int | str | _MissingType = _MISSING) -> int:
    if isinstance(default, _MissingType):
        value = _resolve_env_value(name)
    else:
        value = _resolve_env_value(name, default)
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Environment variable {name} must be an integer") from exc


@overload
def float_env(name: str) -> float: ...


@overload
def float_env(name: str, default: float | int | str) -> float: ...


def float_env(name: str, default: float | int | str | _MissingType = _MISSING) -> float:
    if isinstance(default, _MissingType):
        value = _resolve_env_value(name)
    else:
        value = _resolve_env_value(name, default)
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Environment variable {name} must be a float") from exc


__all__ = ["is_truthy", "bool_env", "str_env", "int_env", "float_env"]
