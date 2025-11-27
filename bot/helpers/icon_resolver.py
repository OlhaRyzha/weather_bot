import os
from datetime import datetime
from config.settings import ASSETS_DIR, ICON_SUNNY


def is_daytime():
    """Return True if current local time is between 6:00 and 19:59."""
    hour = datetime.now().hour
    return 6 <= hour < 20


def get_icon_key(weather_id: int):
    """Map OpenWeather condition ids to asset keys."""
    if 200 <= weather_id <= 232:
        return "wind"

    if 300 <= weather_id <= 321:
        return "drizzle"

    if 500 <= weather_id <= 531:
        return "rainy"

    if 600 <= weather_id <= 622:
        return "snowy"

    if 700 <= weather_id <= 781:
        return "fog"

    if weather_id == 800:
        return "sunny" if is_daytime() else "clear_night"

    if weather_id == 801:
        return "sunny_cloud" if is_daytime() else "cloud_night"

    if 802 <= weather_id <= 804:
        return "sunny_cloud"

    return "sunny"


def resolve_icon_path(icon_key: str):
    icon_path = os.path.join(ASSETS_DIR, f"{icon_key}.png")
    if os.path.exists(icon_path):
        return icon_path

    return ICON_SUNNY
