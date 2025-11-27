import os
from dataclasses import dataclass
from dotenv import load_dotenv

from config.env import bool_env, float_env, int_env, str_env
from config.types import MessagesType

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

ICON_SUNNY = os.path.join(ASSETS_DIR, "sunny.png")
ICON_RAINY = os.path.join(ASSETS_DIR, "rainy.png")

API_TOKEN = os.getenv("API_TOKEN") or ""
WEATHER_API_TOKEN = os.getenv("WEATHER_API_TOKEN") or ""
WEATHER_API_BASE = os.getenv("WEATHER_API_BASE") or ""
DEFAULT_UNITS = "metric"
LLM_URL = os.getenv("LLM_API_URL") or ""
LLM_SYSTEM_INSTRUCTION_TEMPLATE = """
You are a friendly companion assistant for a weather Telegram bot.

Your job is to add a very short tip under the weather forecast.

Rules:
- Reply in English.
- Use 1–2 sentences only (around 15–30 words).
- Address the user by name, for example: "{user_name}, ..." at least once.
- Use the given city, weather description, and general conditions.
- Focus on practical or cozy suggestions:
  what to wear, whether to bring an umbrella, or what to do in that city in such weather.
- Do NOT repeat exact numbers or degrees (the temperature is already shown above).
- Do NOT use emojis or markdown formatting. Plain text only.
- Be positive, empathetic, and to the point.
""".strip()

LLM_PROMPT_TEMPLATE = """
{system_instruction}

Context:
- User name: {user_name}
- City: {city}
- Weather description: {normalized_description}
- Temperature (C, for your understanding only): {temp_c}
- Raw user data (if any): {user_data}

Task:
Write one short, friendly tip for the user based on this weather and location.
""".strip()


MESSAGES: MessagesType = {
    "city_not_found": "⚠️ Could not find the city or the API returned an error.",
    "enter_city": "Please enter a city name (e.g., London).",
    "shortcut_command": "Please enter a shortcut command (e.g., home, work).",
    "msql_disabled": "MySQL shortcut storage is disabled.",
    "msql_ready": "MySQL shortcut storage is ready",
    "msql_pool_error": "MySQL pool is not initialized. Call init_mysql_pool() first.",
    "aiomysql_not_installed": (
        "aiomysql is not installed. Install it to enable MySQL support or disable it "
        "by setting MYSQL_ENABLED=0."
    ),
    "empty_error": "<code>{entity}</code> cannot be empty. Please enter it again:",
    "space_error": (
        "Command must not contain spaces. Try something like <code>home</code> or <code>work</code>."
    ),
    "already_exists": (
        "Shortcut <code>{command}</code> already exists. Please enter another command:"
    ),
    "entered_city": "Great! Now enter a city for <code>{command}</code> (e.g., Lviv):",
    "smth_wrong": "Something went wrong. Please try adding shortcut again.",
    "shortcut_added": "Shortcut added: <code>{command}</code> → <b>{city}</b>",
    "dont_have_shortcuts": "You don't have any shortcuts yet.",
    "provide_valid_city": "Please provide a valid city name.",
    "weather_api_not_configured": "Weather API is not configured.",
    "share_location": "Please share your location from a mobile device 📱",
    "loader_message": "⛅ One moment...",
}


@dataclass(frozen=True)
class MySQLConfig:
    enabled: bool
    host: str
    port: int
    user: str
    password: str
    database: str
    min_pool_size: int
    max_pool_size: int
    connect_timeout: float


def _build_mysql_config() -> MySQLConfig:
    enabled = bool_env("MYSQL_ENABLED", default=False)
    if not enabled:
        return MySQLConfig(
            enabled=False,
            host="",
            port=0,
            user="",
            password="",
            database="",
            min_pool_size=0,
            max_pool_size=0,
            connect_timeout=0.0,
        )

    return MySQLConfig(
        enabled=True,
        host=str_env("MYSQL_HOST"),
        port=int_env("MYSQL_PORT"),
        user=str_env("MYSQL_USER"),
        password=str_env("MYSQL_PASSWORD", default=""),
        database=str_env("MYSQL_DATABASE"),
        min_pool_size=int_env("MYSQL_MIN_POOL"),
        max_pool_size=int_env("MYSQL_MAX_POOL"),
        connect_timeout=float_env("MYSQL_CONNECT_TIMEOUT"),
    )


MYSQL = _build_mysql_config()
