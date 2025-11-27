import aiohttp
import pytest
from bot.weather_clients.llm import client as client_module


class FakeLLMResponse:
    def __init__(self, status, payload):
        self.status = status
        self._payload = payload

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def json(self):
        return self._payload


class FakeLLMSession:
    def __init__(self, response, *, raise_error=False):
        self._response = response
        self._raise_error = raise_error
        self.requests = []

    async def __aenter__(self):
        if self._raise_error:
            raise aiohttp.ClientError("boom")
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    def post(self, url, *, json):
        self.requests.append((url, json))
        if self._raise_error:
            raise aiohttp.ClientError("boom")
        return self._response


def make_session_factory(session):
    class SessionFactory:
        async def __aenter__(self):
            return session

        async def __aexit__(self, exc_type, exc, tb):
            return False

    return SessionFactory


@pytest.mark.anyio("asyncio")
async def test_call_llm_requires_url(monkeypatch):
    monkeypatch.setattr(client_module, "LLM_URL", "")
    assert await client_module.call_llm({"a": "b"}) is None


@pytest.mark.anyio("asyncio")
async def test_call_llm_returns_payload(monkeypatch):
    monkeypatch.setattr(client_module, "LLM_URL", "https://llm")
    response = FakeLLMResponse(200, {"response": "ok"})
    session = FakeLLMSession(response)
    monkeypatch.setattr(
        client_module.aiohttp, "ClientSession", lambda: make_session_factory(session)()
    )

    payload = await client_module.call_llm({"prompt": "hello"})
    assert payload == {"response": "ok"}
    assert session.requests[0][0] == "https://llm/api/generate"


@pytest.mark.anyio("asyncio")
async def test_call_llm_handles_non_200(monkeypatch):
    monkeypatch.setattr(client_module, "LLM_URL", "https://llm")
    response = FakeLLMResponse(500, {"error": "bad"})
    session = FakeLLMSession(response)
    monkeypatch.setattr(
        client_module.aiohttp, "ClientSession", lambda: make_session_factory(session)()
    )

    assert await client_module.call_llm({"prompt": "hello"}) is None


@pytest.mark.anyio("asyncio")
async def test_call_llm_handles_client_error(monkeypatch):
    monkeypatch.setattr(client_module, "LLM_URL", "https://llm")
    session = FakeLLMSession(None, raise_error=True)
    monkeypatch.setattr(
        client_module.aiohttp, "ClientSession", lambda: make_session_factory(session)()
    )

    assert await client_module.call_llm({"prompt": "hello"}) is None
