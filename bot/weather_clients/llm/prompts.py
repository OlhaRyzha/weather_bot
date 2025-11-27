from aiogram.types import Message
from bot.helpers import normalize_text
from bot.helpers.text_formatters import get_full_name
from config.settings import (
    LLM_PROMPT_TEMPLATE,
    LLM_SYSTEM_INSTRUCTION_TEMPLATE,
)


def build_system_instruction(user_name: str):
    return LLM_SYSTEM_INSTRUCTION_TEMPLATE.format(user_name=user_name)


def build_prompt(
    *,
    system_instruction: str,
    user_name: str,
    city: str,
    description: str,
    temp_c: int,
    user_data: dict | None,
):
    normalized_description = normalize_text(description)
    return LLM_PROMPT_TEMPLATE.format(
        system_instruction=system_instruction,
        user_name=user_name,
        city=city,
        normalized_description=normalized_description,
        temp_c=temp_c,
        user_data=user_data,
    )


async def get_payload(
    message: Message,
    *,
    city: str,
    temp_c: int,
    description: str,
    user_data: dict | None = None,
):
    user_name = get_full_name(message.from_user)
    system_instruction = build_system_instruction(user_name=user_name)
    prompt = build_prompt(
        system_instruction=system_instruction,
        user_name=user_name,
        city=city,
        description=description,
        temp_c=temp_c,
        user_data=user_data,
    )

    return {
        "model": "llama3.2:3b",
        "prompt": prompt,
        "stream": False,
    }
