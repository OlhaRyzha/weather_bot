from typing import Mapping, TypeAliasType


LLMPayload = TypeAliasType(
    "LLMPayload", str | list["LLMPayload"] | Mapping[str, "LLMPayload"] | None
)


def extract_advice_text(payload: LLMPayload):
    if not payload:
        return ""

    if isinstance(payload, str):
        return payload.strip()

    if isinstance(payload, list):
        for item in payload:
            text = extract_advice_text(item)
            if text:
                return text
        return ""

    if isinstance(payload, Mapping):
        response = payload.get("response")
        if isinstance(response, str):
            return response.strip()

        content = payload.get("content")
        if isinstance(content, str):
            return content.strip()

        for key in ("message", "text"):
            value = payload.get(key)
            text = extract_advice_text(value)
            if text:
                return text

        choices = payload.get("choices")
        if isinstance(choices, list):
            for choice in choices:
                text = extract_advice_text(choice)
                if text:
                    return text

    return ""
