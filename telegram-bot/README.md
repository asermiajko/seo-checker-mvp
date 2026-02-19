# SEO Checker Telegram Bot

Telegram bot interface for SEO health checks.

## Installation

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Set your Telegram bot token (get it from [@BotFather](https://t.me/BotFather)):

```
BOT_TOKEN=your_token_here
API_URL=http://localhost:8000
```

## Development

```bash
# Run bot
python bot.py

# Run tests
pytest
```

## Commands

- `/start` - Start bot
- `/help` - Show help message
