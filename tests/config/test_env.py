import pytest
from config import env as env_module


def test_is_truthy_and_bool_env(monkeypatch):
    assert env_module.is_truthy("YES") is True
    monkeypatch.setenv("FLAG_TRUE", "Yes")
    monkeypatch.delenv("FLAG_FALSE", raising=False)
    assert env_module.bool_env("FLAG_TRUE") is True
    assert env_module.bool_env("FLAG_FALSE", default=True) is True
    assert env_module.bool_env("FLAG_FALSE", default=False) is False


def test_str_env_required_and_default(monkeypatch):
    monkeypatch.delenv("MISSING", raising=False)
    with pytest.raises(RuntimeError):
        env_module.str_env("MISSING")

    monkeypatch.setenv("NULLABLE", "")
    assert env_module.str_env("NULLABLE") == ""
    assert env_module.str_env("NOT_SET", default=None) == ""
    monkeypatch.setenv("WITH_VALUE", "42")
    assert env_module.str_env("WITH_VALUE") == "42"


def test_int_env_and_errors(monkeypatch):
    monkeypatch.setenv("INT_VALUE", "7")
    assert env_module.int_env("INT_VALUE") == 7

    monkeypatch.setenv("INT_FROM_DEFAULT", "9")
    assert env_module.int_env("INT_FROM_DEFAULT", default="5") == 9

    monkeypatch.setenv("BAD_INT", "abc")
    with pytest.raises(ValueError):
        env_module.int_env("BAD_INT")


def test_float_env_and_errors(monkeypatch):
    monkeypatch.setenv("FLOAT_VALUE", "3.14")
    assert env_module.float_env("FLOAT_VALUE") == pytest.approx(3.14)

    monkeypatch.setenv("FLOAT_DEFAULTED", "2.71")
    assert env_module.float_env("FLOAT_DEFAULTED", default="1.0") == pytest.approx(2.71)

    monkeypatch.setenv("BAD_FLOAT", "oops")
    with pytest.raises(ValueError):
        env_module.float_env("BAD_FLOAT")
