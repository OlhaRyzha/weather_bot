import importlib
import pytest


@pytest.fixture(autouse=True)
def reset_settings():
    yield
    import config.settings as settings_module

    importlib.reload(settings_module)


def _reload_settings(monkeypatch, **env_values):
    for key, value in env_values.items():
        monkeypatch.setenv(key, value)
    import config.settings as settings_module

    return importlib.reload(settings_module)


def test_mysql_config_disabled(monkeypatch):
    module = _reload_settings(monkeypatch, MYSQL_ENABLED="0")
    assert module.MYSQL.enabled is False
    assert module.MYSQL.host == ""


def test_mysql_config_enabled(monkeypatch):
    env = {
        "MYSQL_ENABLED": "1",
        "MYSQL_HOST": "db",
        "MYSQL_PORT": "3306",
        "MYSQL_USER": "user",
        "MYSQL_PASSWORD": "pw",
        "MYSQL_DATABASE": "weather",
        "MYSQL_MIN_POOL": "1",
        "MYSQL_MAX_POOL": "5",
        "MYSQL_CONNECT_TIMEOUT": "3.5",
    }
    module = _reload_settings(monkeypatch, **env)
    cfg = module.MYSQL
    assert cfg.enabled is True
    assert cfg.host == "db"
    assert cfg.port == 3306
    assert cfg.user == "user"
    assert cfg.password == "pw"
    assert cfg.database == "weather"
    assert cfg.min_pool_size == 1
    assert cfg.max_pool_size == 5
    assert cfg.connect_timeout == 3.5
