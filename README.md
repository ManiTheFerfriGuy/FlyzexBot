# Flyzex Guild Application Bot

A Telegram bot that guides prospective members through a short questionnaire and
lets guild admins approve or reject applications directly from Telegram.

## Features

- Applicants answer a configurable set of questions in the bot's DM.
- Admins receive inline review messages with **Accept** or **Reject** buttons.
- Accepted applicants automatically receive the guild invitation code.
- Pending applications are stored on disk so that no answers are lost between
  restarts.

## Project structure

```
bot/
├── config.py      # Customise admin IDs, questions, and invite code here
├── main.py        # Bot entrypoint
└── storage.py     # Minimal JSON-backed persistence layer
```

## Prerequisites

- Python 3.11+
- A Telegram bot token from [@BotFather](https://t.me/BotFather)

## Installation

Create and activate a virtual environment, then install dependencies.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Configuration

1. Export your bot token: `export BOT_TOKEN=123456:ABCDEF`.
2. Open `bot/config.py` and edit:
   - `admin_ids`: Telegram user IDs allowed to review applications.
   - `questions`: The questions asked during the application flow.
   - `invite_code`: The guild invitation code or link sent to accepted members.

## Running the bot

```bash
python -m bot.main
```

The bot uses long polling by default. Deploy it on a server or service that can
run a persistent Python process.

## Next steps

This initial version keeps configuration in code and uses JSON storage. Future
improvements could include:

- Adding an admin command to update questions dynamically.
- Integrating with a database for audit trails.
- Supporting multiple guilds or invite codes based on user responses.
