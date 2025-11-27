from bot.weather_clients.llm.response import extract_advice_text


def test_extract_advice_text_from_string():
    assert extract_advice_text("  Stay cozy!  ") == "Stay cozy!"


def test_extract_advice_text_from_nested_list():
    payload = ["", {"response": " Pack an umbrella. "}]
    assert extract_advice_text(payload) == "Pack an umbrella."


def test_extract_advice_text_returns_empty_for_empty_list():
    assert extract_advice_text([]) == ""


def test_extract_advice_text_from_mapping_variants():
    payload = {
        "message": {"text": "  Layer up.  "},
    }
    assert extract_advice_text(payload) == "Layer up."


def test_extract_advice_text_from_choices():
    payload = {
        "choices": [
            {"message": {"content": ""}},
            {"message": {"content": "  Enjoy the sunshine.  "}},
        ]
    }
    assert extract_advice_text(payload) == "Enjoy the sunshine."


def test_extract_advice_text_handles_missing_payload():
    assert extract_advice_text(None) == ""
