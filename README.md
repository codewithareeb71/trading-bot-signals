# Telegram AI Trading Signal Bot

A modular Python Telegram bot for educational trading signals, analytics, and performance tracking.

## Features
- Real-time market snapshot analysis using technical indicators
- Signals with confidence scoring, trade reasoning, and risk warnings
- Telegram commands: `/start`, `/signal`, `/market`, `/history`, `/help`, `/settings`
- Admin features: broadcasting, statistics, enable/disable signals, user management
- SQLite persistence for signal history and user tracking
- Clean bot interface with a trading disclaimer

## Setup
1. Create a Python environment:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
2. Install dependencies in an isolated virtual environment:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and fill in your bot token and admin IDs.

> Note: Use a dedicated venv for this bot. `python-telegram-bot==20.7` requires `httpx==0.25.2`. If you also need `google-genai`, install it in a separate environment because it requires `httpx>=0.28.1`.

## Running the bot
- Activate the venv and run:
  ```powershell
  .\.venv\Scripts\Activate.ps1
  python main.py
  ```
- Or use the included launch helper on Windows:
  ```powershell
  .\run.ps1
  ```
4. Run the bot:
   ```powershell
   python main.py
   ```

## Commands
- `/start` - Welcome message and disclaimer
- `/signal [symbol]` - Generate a trading signal for a symbol
- `/market [symbol]` - Show market analysis summary
- `/history [limit]` - View recent signal history
- `/settings` - Show bot settings and user preferences
- `/help` - Command help

## Admin Commands
- `/broadcast <message>` - Send a message to all registered users
- `/stats` - View bot statistics and signal counts
- `/toggle_signals <on|off>` - Enable or disable signal generation
- `/users` - List registered users

## Notes
- This bot is educational and analytical only.
- Signals are probability-based estimates, not trading advice.
- Never trade with money you cannot afford to lose.
