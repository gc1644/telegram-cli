# telegram-cli

Super minimal terminal Telegram client.  
Just text messages, chat list, and basic send/receive.

Built with Python + TDLib (python-telegram).

## Features

- Login with phone number
- List recent chats
- Open chat and view recent messages
- Send text messages
- Vi-mode input + history

## Installation

```bash
git clone https://github.com/gc1644/telegram-cli
cd telegram-cli
run install.sh for dependencies
python3 -m venv venv
source venv/bin/activate

pip install python-telegram prompt_toolkit
