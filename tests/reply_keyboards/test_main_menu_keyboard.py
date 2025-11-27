from bot.reply_keyboards.main_menu_keyboard import (
    MAIN_BTN_ADD_SHORTCUT,
    MAIN_BTN_CITY,
    MAIN_BTN_LOCATION,
    MAIN_BTN_SHOW_SHORTCUT,
    build_main_kb,
)


def test_build_main_keyboard_without_shortcuts():
    markup = build_main_kb([])
    assert markup.resize_keyboard is True
    texts = [[button.text for button in row] for row in markup.keyboard]
    assert texts[0] == [MAIN_BTN_CITY, MAIN_BTN_LOCATION]
    assert texts[1] == [MAIN_BTN_ADD_SHORTCUT]
    assert texts[2] == [MAIN_BTN_SHOW_SHORTCUT]
    assert markup.keyboard[0][1].request_location is True


def test_build_main_keyboard_with_shortcuts():
    markup = build_main_kb(["home", "work", "gym"])
    all_texts = [button.text for row in markup.keyboard for button in row]
    assert "Home" in all_texts
    assert "Gym" in all_texts
