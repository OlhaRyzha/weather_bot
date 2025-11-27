from typing import Literal

MessagesItemType = Literal[
    "city_not_found",
    "enter_city",
    "shortcut_command",
    "msql_disabled",
    "msql_ready",
    "empty_error",
    "space_error",
    "already_exists",
    "entered_city",
    "smth_wrong",
    "shortcut_added",
    "dont_have_shortcuts",
    "msql_pool_error",
    "aiomysql_not_installed",
    "provide_valid_city",
    "weather_api_not_configured",
    "share_location",
    "loader_message",
]

MessagesType = dict[MessagesItemType, str]
QueryParamType = dict[str, str | int | float]
