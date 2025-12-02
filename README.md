# Weather Bot(@olha_ryzha_weather_bot)

Telegram bot built with Aiogram 3 that shows the current weather, adds a short LLM hint, and lets users save shortcut commands for favorite cities. Works with OpenWeather and supports location sharing or typed city names.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Running the bot

```bash
python main.py
```

## Testing

Run the test suite with:

```bash
pytest
```
Test Coverage:

```bash
pytest --cov=bot --cov=config --cov-report=term-missing
pytest --cov=bot --cov=config --cov-report=html
```
