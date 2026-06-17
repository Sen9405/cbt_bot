# 🧠 CBT Bot (Cognitive Behavioral Therapy)

[![Tests](https://github.com/Sen9405/cbt_bot/workflows/Tests/badge.svg)](https://github.com/Sen9405/cbt_bot/actions)

A Telegram bot for keeping a Cognitive Behavioral Therapy (CBT) journal.

## Features

- **🧠 CBT Journal** — record situations, automatic thoughts, emotions, and reactions
- **📋 Daily Plans** — plan your day and track task completion
- **🏆 Achievements** — keep a list of personal wins
- **📊 Excel Export** — export your data to .xlsx
- **🔓 Free Tier** — up to 20 records, plans, and achievements for free users
- **👑 Admin Access** — unlimited usage for the admin

## Getting Started

```bash
git clone https://github.com/Sen9405/cbt_bot.git
cd cbt_bot
cp .env.example .env
# Edit .env with your tokens and IDs
pip install -r requirements.txt
python3 cbt_bot.py
```

### Environment Variables

All configuration is done through `.env`. See `.env.example` for a template:

| Variable | Description |
|---|---|
| `CBT_BOT_TOKEN` | Telegram bot token from [@BotFather](https://t.me/botfather) |
| `ADMIN_TG_ID` | Your Telegram user ID (unlimited access) |

Optional for MAX (VK Business) bridge:

| Variable | Description |
|---|---|
| `MAX_BOT_TOKEN` | MAX bot authentication token |
| `MAX_BOT_ADMIN_ID` | Your MAX user ID (for user mapping) |

## Dependencies

```
pyTelegramBotAPI
python-dotenv
openpyxl
requests
```

## Running Tests

```bash
pytest tests/ -v
```

Tests run automatically via GitHub Actions on every push.

## License

MIT
