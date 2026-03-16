# ════════════════════════════════════════
#  Satoru — م7: الاختصارات والميمز
# ════════════════════════════════════════
import os, asyncio
from satoru import client
from telethon import events
from database import db

MEDIA_DIR = "saved_media"
os.makedirs(MEDIA_DIR, exist_ok=True)


def _key(name: str) -> str:
    return f"shortcut:{name.lower()}"


@client.on(events.NewMessage(outgoing=True, pattern=r"^\.اضف (.+)$"))
async def add_shortcut(event):
    await event.delete()
    name  = event.pattern_match.group(1).strip()
    reply = await event.get_reply_message()
    if not reply:
        return await event.respond("يجب الرد على الرسالة/الوسيطة المراد حفظها")

    data = {"text": reply.text or "", "file": None}
    if reply.media:
        file_path = os.path.join(MEDIA_DIR, f"{name}_{reply.id}")
        try:
            file_path = await reply.download_media(file=file_path)
            data["file"] = file_path
        except Exception as e:
            return await event.respond(f"خطأ في التحميل: {e}")

    db.set(_key(name), data)
    db.sadd("shortcuts", name.lower())
    await event.respond(f"تم حفظ الاختصار: `{name}`")


@client.on(events.NewMessage(outgoing=True, pattern=r"^\.احذف (.+)$"))
async def del_shortcut(event):
    await event.delete()
    name = event.pattern_match.group(1).strip()
    if db.exists(_key(name)):
        data = db.get(_key(name))
        if data and data.get("file") and os.path.exists(data["file"]):
            try: os.remove(data["file"])
            except Exception: pass
        db.delete(_key(name))
        db.srem("shortcuts", name.lower())
        await event.respond(f"تم حذف الاختصار: `{name}`")
    else:
        await event.respond(f"لا يوجد اختصار باسم: `{name}`")


@client.on(events.NewMessage(outgoing=True, pattern=r"^\.اختصاراتي$"))
async def list_shortcuts(event):
    await event.delete()
    shorts = db.smembers("shortcuts")
    if not shorts:
        return await event.respond("لا توجد اختصارات محفوظة")
    text = "**اختصاراتي:**\n\n"
    for i, s in enumerate(sorted(shorts), 1):
        text += f"  `{i}.`  `.{s}`\n"
    await event.respond(text)


@client.on(events.NewMessage(outgoing=True, pattern=r"^\.مسح الاختصارات$"))
async def clear_shortcuts(event):
    await event.delete()
    for name in list(db.smembers("shortcuts")):
        data = db.get(_key(name))
        if data and data.get("file"):
            try: os.remove(data["file"])
            except Exception: pass
        db.delete(_key(name))
    db.sdelete("shortcuts")
    await event.respond("تم مسح جميع الاختصارات")


@client.on(events.NewMessage(outgoing=True, pattern=r"^\.([^\s\.].*)$"))
async def send_shortcut(event):
    name = event.pattern_match.group(1).strip().lower()

    import re
    if re.match(r"^م\d+$", name):
        return
    if not db.exists(_key(name)):
        return

    await event.delete()
    data = db.get(_key(name))
    if not data:
        return

    try:
        if data.get("file") and os.path.exists(data["file"]):
            await client.send_file(event.chat_id, data["file"], caption=data.get("text") or "")
        elif data.get("text"):
            await client.send_message(event.chat_id, data["text"])
    except Exception as e:
        await event.respond(f"خطأ: {e}")
