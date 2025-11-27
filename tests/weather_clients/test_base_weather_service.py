import types
import aiohttp
import pytest
from aiogram.types import FSInputFile, ReplyKeyboardMarkup
from bot.weather_clients.base_weather_service import (
    build_caption_payload,
    perform_request,
    send_weather_response,
)
from config.settings import DEFAULT_UNITS, ICON_SUNNY, MESSAGES


class FakeResponse:
    def __init__(self, status, payload):
        self.status = status
        self._payload = payload

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def json(self):
        return self._payload


class FakeSession:
    def __init__(self, response):
        self._response = response
        self.last_call = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    def get(self, base, *, params, ssl):
        self.last_call = (base, params, ssl)
        return self._response


@pytest.mark.anyio("asyncio")
async def test_send_weather_response_requires_config(monkeypatch, fake_message_factory):
    message = fake_message_factory()
    monkeypatch.setattr(
        "bot.weather_clients.base_weather_service.WEATHER_API_TOKEN", ""
    )
    monkeypatch.setattr("bot.weather_clients.base_weather_service.WEATHER_API_BASE", "")

    await send_weather_response(message, query_params={})

    assert len(message.answers) == 1
    assert message.answers[0]["text"] == "Weather API is not configured."


@pytest.mark.anyio("asyncio")
async def test_send_weather_response_handles_api_errors(
    monkeypatch,
    fake_message_factory,
):
    message = fake_message_factory()
    monkeypatch.setattr(
        "bot.weather_clients.base_weather_service.WEATHER_API_TOKEN", "token"
    )
    monkeypatch.setattr(
        "bot.weather_clients.base_weather_service.WEATHER_API_BASE",
        "https://example.com",
    )

    async def fake_request(params):
        assert params["appid"] == "token"
        assert params["units"] == "metric"
        return None

    monkeypatch.setattr(
        "bot.weather_clients.base_weather_service.perform_request",
        fake_request,
    )

    dummy_markup = ReplyKeyboardMarkup(keyboard=[])

    await send_weather_response(
        message,
        query_params={"q": "kyiv"},
        reply_markup=dummy_markup,
    )

    assert len(message.answers) == 1
    assert message.answers[0]["text"] == MESSAGES["city_not_found"]
    assert message.answers[0]["reply_markup"] is dummy_markup


@pytest.mark.anyio("asyncio")
async def test_send_weather_response_sends_photo_on_success(
    monkeypatch,
    fake_message_factory,
):
    message = fake_message_factory()
    monkeypatch.setattr(
        "bot.weather_clients.base_weather_service.WEATHER_API_TOKEN", "token"
    )
    monkeypatch.setattr(
        "bot.weather_clients.base_weather_service.WEATHER_API_BASE",
        "https://example.com",
    )

    async def fake_request(params):
        return {
            "name": "Kyiv",
            "main": {"temp": 5.4},
            "weather": [{"id": 800, "description": "clear sky"}],
        }

    monkeypatch.setattr(
        "bot.weather_clients.base_weather_service.perform_request",
        fake_request,
    )
    monkeypatch.setattr(
        "bot.weather_clients.base_weather_service.resolve_icon_path",
        lambda _: ICON_SUNNY,
    )

    dummy_markup = ReplyKeyboardMarkup(keyboard=[])

    await send_weather_response(
        message,
        query_params={"q": "kyiv"},
        reply_markup=dummy_markup,
    )

    assert len(message.photo_answers) == 1
    call = message.photo_answers[0]
    assert isinstance(call["photo"], FSInputFile)
    assert "Kyiv" in call["caption"]
    assert "Temperature" in call["caption"]
    assert call["reply_markup"] is dummy_markup


def test_build_caption_payload_prefers_display_name(monkeypatch):
    monkeypatch.setattr(
        "bot.weather_clients.base_weather_service.resolve_icon_path",
        lambda key: f"/tmp/{key}.png",
    )

    data = {
        "name": "kyiv",
        "main": {"temp": 4.6},
        "weather": [{"id": 500, "description": "light rain"}],
    }

    caption, icon_path, city_name, temp, description = build_caption_payload(
        data,
        fallback_city="lviv",
        display_name="Home Base",
    )

    assert "<b>Home Base</b>" in caption
    assert city_name == "Home Base"
    assert temp == 5
    assert description == "light rain"
    assert icon_path == "/tmp/rainy.png"


def test_build_caption_payload_handles_missing_values():
    data = {
        "weather": [{}],
    }

    caption, icon_path, city_name, temp, description = build_caption_payload(
        data,
        fallback_city="unknown",
    )

    assert "<b>Unknown</b>" in caption
    assert city_name == "unknown"
    assert temp == 0
    assert description == ""
    assert icon_path == ICON_SUNNY


@pytest.mark.anyio("asyncio")
async def test_send_weather_response_appends_llm_advice(
    monkeypatch,
    fake_message_factory,
):
    message = fake_message_factory()
    monkeypatch.setattr(
        "bot.weather_clients.base_weather_service.WEATHER_API_TOKEN", "token"
    )
    monkeypatch.setattr(
        "bot.weather_clients.base_weather_service.WEATHER_API_BASE",
        "https://example.com",
    )

    async def fake_request(params):
        assert params["appid"] == "token"
        assert params["units"] == DEFAULT_UNITS
        return {
            "name": "Kyiv",
            "main": {"temp": 8.2},
            "weather": [{"id": 801, "description": "few clouds"}],
        }

    monkeypatch.setattr(
        "bot.weather_clients.base_weather_service.perform_request", fake_request
    )

    advice_calls = {}

    async def fake_advice(message_arg, *, city, temp_c, description, user_data):
        advice_calls.update(
            {
                "message": message_arg,
                "city": city,
                "temp_c": temp_c,
                "description": description,
                "user_data": user_data,
            }
        )
        return "Bring a light jacket."

    monkeypatch.setattr(
        "bot.weather_clients.base_weather_service.get_llm_advice_text",
        fake_advice,
    )
    monkeypatch.setattr(
        "bot.weather_clients.base_weather_service.resolve_icon_path",
        lambda _: ICON_SUNNY,
    )

    await send_weather_response(message, query_params={"q": "kyiv"})

    assert advice_calls["message"] is message
    assert advice_calls["city"] == "Kyiv"
    assert advice_calls["temp_c"] == 8
    assert advice_calls["description"] == "few clouds"
    assert advice_calls["user_data"] == {"units": DEFAULT_UNITS}

    assert len(message.photo_answers) == 1
    caption = message.photo_answers[0]["caption"]
    assert "Bring a light jacket." in caption
    assert caption.count("\n\n") == 1


@pytest.mark.anyio("asyncio")
async def test_send_weather_response_deletes_loader_on_failure(
    monkeypatch,
    fake_message_factory,
):
    message = fake_message_factory()
    monkeypatch.setattr(
        "bot.weather_clients.base_weather_service.WEATHER_API_TOKEN", "token"
    )
    monkeypatch.setattr(
        "bot.weather_clients.base_weather_service.WEATHER_API_BASE",
        "https://example.com",
    )

    async def fake_request(params):
        return {
            "name": "Kyiv",
            "main": {"temp": 2},
            "weather": [{"id": 800, "description": "clear"}],
        }

    monkeypatch.setattr(
        "bot.weather_clients.base_weather_service.perform_request", fake_request
    )

    async def fake_advice(*args, **kwargs):
        return ""

    monkeypatch.setattr(
        "bot.weather_clients.base_weather_service.get_llm_advice_text",
        fake_advice,
    )
    monkeypatch.setattr(
        "bot.weather_clients.base_weather_service.resolve_icon_path",
        lambda _: ICON_SUNNY,
    )
    monkeypatch.setitem(MESSAGES, "loader_message", "Loading…")

    loader_state = {"deleted": False}
    original_answer = message.answer

    async def fake_answer(self, text, **kwargs):
        result = await original_answer(text, **kwargs)
        if text == "Loading…":
            # provide a simple stub with delete()
            class LoaderMessage:
                def __init__(self, state):
                    self._state = state

                async def delete(self):
                    self._state["deleted"] = True

            return LoaderMessage(loader_state)
        return result

    message.answer = types.MethodType(fake_answer, message)

    async def failing_photo(**kwargs):
        raise RuntimeError("boom")

    message.answer_photo = failing_photo

    with pytest.raises(RuntimeError):
        await send_weather_response(message, query_params={"q": "kyiv"})

    assert loader_state["deleted"] is True


@pytest.mark.anyio("asyncio")
async def test_perform_request_returns_payload(monkeypatch):
    response = FakeResponse(status=200, payload={"ok": True})
    session = FakeSession(response)

    class ClientSessionFactory:
        async def __aenter__(self):
            return session

        async def __aexit__(self, exc_type, exc, tb):
            return False

    monkeypatch.setattr(
        "bot.weather_clients.base_weather_service.aiohttp.ClientSession",
        lambda: ClientSessionFactory(),
    )

    result = await perform_request({"q": "kyiv"})
    assert result == {"ok": True}
    assert session.last_call is not None
    assert session.last_call[1]["q"] == "kyiv"


@pytest.mark.anyio("asyncio")
async def test_perform_request_handles_non_200(monkeypatch):
    response = FakeResponse(status=500, payload={"error": True})
    session = FakeSession(response)

    class ClientSessionFactory:
        async def __aenter__(self):
            return session

        async def __aexit__(self, exc_type, exc, tb):
            return False

    monkeypatch.setattr(
        "bot.weather_clients.base_weather_service.aiohttp.ClientSession",
        lambda: ClientSessionFactory(),
    )

    result = await perform_request({"q": "kyiv"})
    assert result is None


@pytest.mark.anyio("asyncio")
async def test_send_weather_response_handles_client_error(
    monkeypatch, fake_message_factory
):
    message = fake_message_factory()
    monkeypatch.setattr(
        "bot.weather_clients.base_weather_service.WEATHER_API_TOKEN", "token"
    )
    monkeypatch.setattr(
        "bot.weather_clients.base_weather_service.WEATHER_API_BASE",
        "https://example.com",
    )

    async def failing_request(params):
        raise aiohttp.ClientError()

    monkeypatch.setattr(
        "bot.weather_clients.base_weather_service.perform_request", failing_request
    )

    await send_weather_response(message, query_params={"q": "kyiv"})

    assert message.answers[0]["text"] == MESSAGES["city_not_found"]
