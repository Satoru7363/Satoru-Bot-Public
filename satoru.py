# ════════════════════════════════════════
#  Satoru — Client Instance
# ════════════════════════════════════════
from telethon import TelegramClient
from telethon.sessions import StringSession
from config import API_ID, API_HASH, SESSION

if SESSION and len(SESSION) > 20:
    client = TelegramClient(StringSession(SESSION), API_ID, API_HASH)
else:
    client = TelegramClient("satoru_session", API_ID, API_HASH)
