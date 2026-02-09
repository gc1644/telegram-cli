import asyncio
import json
import os
from telegram.client import Telegram
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys

# ──────────────────────────────────────
#  Change these!
API_ID = 1234567          # ← your api_id
API_HASH = "your_api_hash_here"  # ← your api_hash
PHONE = "+1234567890"     # your phone number
# ──────────────────────────────────────

# Where TDLib will store data (sessions, cache, etc.)
TDATA_DIR = os.path.expanduser("~/.mytelegram-cli")
os.makedirs(TDATA_DIR, exist_ok=True)

tg = None
current_chat_id = None
chat_list = []           # list of chat ids
chat_titles = {}         # id → title

bindings = KeyBindings()

@bindings.add(Keys.ControlQ)
def _(event):
    event.app.exit(result="quit")

async def login():
    global tg
    tg = Telegram(
        api_id=API_ID,
        api_hash=API_HASH,
        phone=PHONE,
        tdlib_path=None,                    # auto-detect
        files_directory=TDATA_DIR,
        no_updates=False,
    )

    print("Logging in...")
    await tg.login()  # handles code input + 2FA if needed
    print("Logged in!")

async def load_chats(limit=30):
    global chat_list, chat_titles
    res = await tg.get_chats(limit=limit)
    chat_list = res["chat_ids"]
    
    for chat_id in chat_list:
        chat = await tg.get_chat(chat_id)
        title = chat.get("title") or chat.get("username", f"ID {chat_id}")
        chat_titles[chat_id] = title

    print("\nRecent chats:")
    for i, cid in enumerate(chat_list, 1):
        print(f"  {i:2d}  {chat_titles[cid]}")

async def show_messages(chat_id, limit=20):
    print(f"\n--- {chat_titles.get(chat_id, chat_id)} ---")
    res = await tg.get_chat_history(chat_id=chat_id, limit=limit)
    messages = res["messages"][::-1]  # newest last
    
    for msg in messages:
        sender = msg.get("sender_id", {}).get("user_id", "???")
        text = msg.get("content", {}).get("text", {}).get("text", "[no text]")
        print(f"{sender}: {text[:80]}{'...' if len(text)>80 else ''}")

async def send_text(chat_id, text):
    if not text.strip():
        return
    await tg.send_message(chat_id=chat_id, text=text)
    print("→ sent")

async def main_loop():
    global current_chat_id
    
    session = PromptSession(
        history=FileHistory(os.path.expanduser("~/.mytelegram-cli/history")),
        enable_open_in_editor=True,
        multiline=False,
        key_bindings=bindings,
    )
    
    while True:
        try:
            cmd = await asyncio.to_thread(
                lambda: session.prompt(">>> ", vi_mode=True)
            )
            cmd = cmd.strip()
            
            if cmd in ("q", "quit", "exit"):
                break
            elif cmd == "chats":
                await load_chats()
            elif cmd.startswith("open "):
                try:
                    idx = int(cmd.split()[1]) - 1
                    current_chat_id = chat_list[idx]
                    await show_messages(current_chat_id)
                except:
                    print("Invalid chat number")
            elif cmd == "refresh":
                if current_chat_id:
                    await show_messages(current_chat_id)
            elif current_chat_id and cmd:
                await send_text(current_chat_id, cmd)
            else:
                print("Commands:")
                print("  chats          → list chats")
                print("  open <number>  → open chat")
                print("  refresh        → reload messages")
                print("  q / quit       → exit")
                print("  just type      → send message (if chat open)")
                
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")

    await tg.stop()
    print("Goodbye 👋")

if __name__ == "__main__":
    asyncio.run(login())
    asyncio.run(main_loop())
