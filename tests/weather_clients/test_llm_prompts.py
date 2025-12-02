import pytest
from bot.weather_clients.llm import prompts


def test_build_system_instruction_injects_user_name():
    instruction = prompts.build_system_instruction(user_name="Alex")
    assert "Alex" in instruction
    assert "friendly companion" in instruction


def test_build_prompt_normalizes_description_and_embeds_context():
    prompt = prompts.build_prompt(
        system_instruction="SYS",
        user_name="Jane Doe",
        city="Kyiv",
        description="  Light RAIN ",
        temp_c=9,
        user_data={"units": "metric"},
    )

    assert prompt.startswith("SYS")
    assert "City: Kyiv" in prompt
    assert "light rain" in prompt
    assert "Temperature (C, for your understanding only): 9" in prompt
    assert "{'units': 'metric'}" in prompt


@pytest.mark.anyio("asyncio")
async def test_get_payload_assembles_model_request(monkeypatch, fake_message_factory):
    message = fake_message_factory()

    monkeypatch.setattr(
        prompts, "get_full_name", lambda user: f"Captain {user.first_name}"
    )

    payload = await prompts.get_payload(
        message,
        city="Lviv",
        temp_c=1,
        description="Foggy",
        user_data={"locale": "ua"},
    )

    assert payload["model"] == "llama-3.1-70b-versatile"
    assert payload["stream"] is False

    messages = payload["messages"]
    assert isinstance(messages, list)
    assert len(messages) == 2

    system_msg = messages[0]
    user_msg = messages[1]

    assert system_msg["role"] == "system"
    assert user_msg["role"] == "user"

    content = user_msg["content"]
    assert "Captain Jane" in content
    assert "City: Lviv" in content
    assert "foggy" in content.lower()
    assert "{'locale': 'ua'}" in content
