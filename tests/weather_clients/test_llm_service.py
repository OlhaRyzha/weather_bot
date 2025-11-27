import importlib
import pytest
import bot.weather_clients.llm_service as _llm_service_module


@pytest.fixture
def llm_service_module():
    return importlib.reload(_llm_service_module)


@pytest.mark.anyio("asyncio")
async def test_get_llm_advice_text_fetches_once_for_same_request(
    monkeypatch,
    fake_message_factory,
    llm_service_module,
):
    module = llm_service_module
    message = fake_message_factory()

    calls = {"payload": 0, "call_llm": 0, "extract": 0}

    async def fake_payload(message_arg, **kwargs):
        calls["payload"] += 1
        assert message_arg is message
        assert kwargs["city"] == "Kyiv"
        assert kwargs["temp_c"] == 12
        assert kwargs["description"] == "windy"
        assert kwargs["user_data"] == {"units": "metric"}
        return {"prompt": "payload"}

    async def fake_call_llm(payload):
        calls["call_llm"] += 1
        assert payload == {"prompt": "payload"}
        return {"response": "Tip"}

    def fake_extract(data_ai):
        calls["extract"] += 1
        assert data_ai == {"response": "Tip"}
        return "Carry an umbrella."

    monkeypatch.setattr(module, "get_payload", fake_payload)
    monkeypatch.setattr(module, "call_llm", fake_call_llm)
    monkeypatch.setattr(module, "extract_advice_text", fake_extract)

    first = await module.get_llm_advice_text(
        message,
        city="Kyiv",
        temp_c=12,
        description="windy",
        user_data={"units": "metric"},
    )
    second = await module.get_llm_advice_text(
        message,
        city="Kyiv",
        temp_c=12,
        description="windy",
        user_data={"units": "metric"},
    )

    assert first == "Carry an umbrella."
    assert second == "Carry an umbrella."
    assert calls == {"payload": 1, "call_llm": 1, "extract": 1}


@pytest.mark.anyio("asyncio")
async def test_get_llm_advice_text_includes_request_context_in_cache_key(
    monkeypatch,
    fake_message_factory,
    llm_service_module,
):
    module = llm_service_module
    message = fake_message_factory()

    payload_history = []

    async def fake_payload(message_arg, **kwargs):
        payload_history.append(kwargs["description"])
        return {"prompt": kwargs["description"]}

    async def fake_call_llm(payload):
        return {"response": payload["prompt"]}

    def fake_extract(data_ai):
        return data_ai["response"]

    monkeypatch.setattr(module, "get_payload", fake_payload)
    monkeypatch.setattr(module, "call_llm", fake_call_llm)
    monkeypatch.setattr(module, "extract_advice_text", fake_extract)

    windy = await module.get_llm_advice_text(
        message,
        city="Kyiv",
        temp_c=3,
        description="windy",
        user_data=None,
    )
    breezy = await module.get_llm_advice_text(
        message,
        city="Kyiv",
        temp_c=3,
        description="breezy",  # different description breaks the cache
        user_data=None,
    )

    assert windy == "windy"
    assert breezy == "breezy"
    assert payload_history == ["windy", "breezy"]


@pytest.mark.anyio("asyncio")
async def test_send_llm_advice_sends_message_on_text(
    monkeypatch,
    fake_message_factory,
    llm_service_module,
):
    module = llm_service_module
    message = fake_message_factory()

    async def fake_advice(message_arg, **kwargs):
        assert message_arg is message
        return "Stay warm!"

    monkeypatch.setattr(module, "get_llm_advice_text", fake_advice)

    response = await module.send_llm_advice(
        message,
        city="Oslo",
        temp_c=-5,
        description="snow",
        reply_markup="kb",
        user_data={"units": "metric"},
    )

    assert response == "Stay warm!"
    assert len(message.answers) == 1
    assert message.answers[0]["text"] == "Stay warm!"
    assert message.answers[0]["reply_markup"] == "kb"


@pytest.mark.anyio("asyncio")
async def test_send_llm_advice_skips_reply_when_empty(
    monkeypatch,
    fake_message_factory,
    llm_service_module,
):
    module = llm_service_module
    message = fake_message_factory()

    async def fake_advice(message_arg, **kwargs):
        assert message_arg is message
        return ""

    monkeypatch.setattr(module, "get_llm_advice_text", fake_advice)

    response = await module.send_llm_advice(
        message,
        city="Riga",
        temp_c=1,
        description="mist",
        reply_markup=None,
        user_data=None,
    )

    assert response == ""
    assert message.answers == []
