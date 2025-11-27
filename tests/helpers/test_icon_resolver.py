from types import SimpleNamespace
import pytest
from bot.helpers import icon_resolver


def _stub_datetime(hour: int):
    class _FakeDatetime:
        @classmethod
        def now(cls):
            return SimpleNamespace(hour=hour)

    return _FakeDatetime


def test_is_daytime_respects_hours(monkeypatch):
    monkeypatch.setattr(icon_resolver, "datetime", _stub_datetime(9))
    assert icon_resolver.is_daytime() is True

    monkeypatch.setattr(icon_resolver, "datetime", _stub_datetime(23))
    assert icon_resolver.is_daytime() is False


@pytest.mark.parametrize(
    "weather_id,expected",
    [
        (201, "wind"),
        (310, "drizzle"),
        (520, "rainy"),
        (611, "snowy"),
        (721, "fog"),
        (900, "sunny"),
    ],
)
def test_get_icon_key_ranges(weather_id, expected):
    assert icon_resolver.get_icon_key(weather_id) == expected


def test_get_icon_key_respects_daytime(monkeypatch):
    monkeypatch.setattr(icon_resolver, "is_daytime", lambda: True)
    assert icon_resolver.get_icon_key(800) == "sunny"
    assert icon_resolver.get_icon_key(801) == "sunny_cloud"

    monkeypatch.setattr(icon_resolver, "is_daytime", lambda: False)
    assert icon_resolver.get_icon_key(800) == "clear_night"
    assert icon_resolver.get_icon_key(801) == "cloud_night"


def test_resolve_icon_path_returns_asset(monkeypatch, tmp_path):
    monkeypatch.setattr(icon_resolver, "ASSETS_DIR", str(tmp_path))
    monkeypatch.setattr(icon_resolver, "ICON_SUNNY", "fallback.png")

    target = tmp_path / "rainy.png"
    target.write_bytes(b"")

    assert icon_resolver.resolve_icon_path("rainy") == str(target)


def test_resolve_icon_path_falls_back(monkeypatch, tmp_path):
    monkeypatch.setattr(icon_resolver, "ASSETS_DIR", str(tmp_path))
    monkeypatch.setattr(icon_resolver, "ICON_SUNNY", "fallback.png")

    assert icon_resolver.resolve_icon_path("unknown") == "fallback.png"
