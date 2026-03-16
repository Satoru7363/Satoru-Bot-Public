# ════════════════════════════════════════
#  Satoru — م11: النشر التلقائي والسبام
# ════════════════════════════════════════
import asyncio
from satoru import client
from telethon import events

_tasks: dict[str, asyncio.Task] = {}


def _cancel_all():
    for t in list(_tasks.values()):
        if not t.done(): t.cancel()
    _tasks.clear()


def _cancel(name: str):
    task = _tasks.pop(name, None)
    if task and not task.done(): task.cancel()


def _register(name: str, coro):
    _cancel(name)
    task = asyncio.get_event_loop().create_task(coro)
    _tasks[name] = task
    return task


async def _send(chat_id, message):
    try:
        if message.media:
            await client.send_file(chat_id, message.media, caption=message.text or "")
        else:
            await client.send_message(chat_id, message.text)
    except Exception:
        pass


# ── .نشر ثواني @معرف (بالرد) ──────────────────────────────────
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.نشر (\d+) (@?\S+)$"))
async def broadcast_single(event):
    await event.delete()
    seconds = int(event.pattern_match.group(1))
    target  = event.pattern_match.group(2)
    message = await event.get_reply_message()
    if not message:
        return await event.respond("يجب الرد على رسالة")
    try:
        chat = await client.get_entity(target)
    except Exception as e:
        return await event.respond(str(e))

    async def _loop():
        while True:
            await _send(chat.id, message)
            await asyncio.sleep(seconds)

    _register("نشر", _loop())
    await event.respond(f"بدأ النشر في `{target}` كل `{seconds}` ثانية\nللإيقاف: `.ايقاف النشر`")


# ── .نشر الكروبات ثواني (بالرد) ──────────────────────────────────
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.نشر الكروبات (\d+)$"))
async def broadcast_all_groups(event):
    await event.delete()
    seconds = int(event.pattern_match.group(1))
    message = await event.get_reply_message()
    if not message:
        return await event.respond("يجب الرد على رسالة")
    chats = [d for d in await client.get_dialogs() if d.is_group]

    async def _loop():
        while True:
            for chat in chats:
                await _send(chat.id, message)
                await asyncio.sleep(0.5)
            await asyncio.sleep(seconds)

    _register("نشر الكروبات", _loop())
    await event.respond(f"بدأ النشر في {len(chats)} مجموعة كل `{seconds}` ثانية")


# ── .بلش ثواني (بالرد) ─────────────────────────────────────────
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.بلش (\d+)$"))
async def repeat_msg(event):
    await event.delete()
    seconds = int(event.pattern_match.group(1))
    message = await event.get_reply_message()
    if not message:
        return await event.respond("يجب الرد على رسالة")
    chat_id = event.chat_id

    async def _loop():
        while True:
            await _send(chat_id, message)
            await asyncio.sleep(seconds)

    _register("بلش", _loop())
    await event.respond(f"بدأ التكرار كل `{seconds}` ثانية\nللإيقاف: `.ايقاف النشر`")


# ── .نقط ثواني (بالرد) ─────────────────────────────────────────
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.نقط (\d+)$"))
async def dot_spam(event):
    await event.delete()
    seconds  = int(event.pattern_match.group(1))
    reply    = await event.get_reply_message()
    if not reply:
        return await event.respond("يجب الرد على رسالة")
    chat_id  = event.chat_id
    reply_id = reply.id

    async def _loop():
        while True:
            try:
                await client.send_message(chat_id, ".", reply_to=reply_id)
            except Exception:
                pass
            await asyncio.sleep(seconds)

    _register("نقط", _loop())
    await event.respond(f"بدأ السبام كل `{seconds}` ثانية\nللإيقاف: `.ايقاف السبام`")


# ── .سبام جملة (حرف بحرف) ──────────────────────────────────────
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.سبام (.+)$"))
async def char_spam(event):
    await event.delete()
    text    = event.pattern_match.group(1)
    chat_id = event.chat_id

    async def _loop():
        for ch in text:
            await client.send_message(chat_id, ch)
            await asyncio.sleep(0.3)
        _tasks.pop("سبام", None)

    _register("سبام", _loop())


# ── .وسبام جملة (كلمة بكلمة) ──────────────────────────────────
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.وسبام (.+)$"))
async def word_spam(event):
    await event.delete()
    text    = event.pattern_match.group(1)
    chat_id = event.chat_id

    async def _loop():
        for word in text.split():
            await client.send_message(chat_id, word)
            await asyncio.sleep(0.5)
        _tasks.pop("وسبام", None)

    _register("وسبام", _loop())


# ── .تكرار عدد جملة ──────────────────────────────────────────
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.تكرار (\d+) (.+)$"))
async def repeat_text(event):
    await event.delete()
    count   = min(int(event.pattern_match.group(1)), 50)
    text    = event.pattern_match.group(2)
    chat_id = event.chat_id

    async def _loop():
        for _ in range(count):
            await client.send_message(chat_id, text)
            await asyncio.sleep(0.5)
        _tasks.pop("تكرار", None)

    _register("تكرار", _loop())


# ── .خاص (بالرد) — مرة واحدة ──────────────────────────────────
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.خاص$"))
async def broadcast_private(event):
    await event.delete()
    message = await event.get_reply_message()
    if not message:
        return await event.respond("يجب الرد على رسالة")
    dialogs = [d for d in await client.get_dialogs() if d.is_user]
    count   = 0
    for d in dialogs:
        await _send(d.id, message)
        count += 1
        await asyncio.sleep(0.5)
    await event.respond(f"تم الإرسال لـ `{count}` محادثة خاصة")


# ══════════════════════════════════════
#  الإيقاف
# ══════════════════════════════════════

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.ايقاف النشر$"))
async def stop_broadcast(event):
    keys    = ["نشر", "نشر الكروبات", "بلش"]
    stopped = [k for k in keys if k in _tasks]
    for k in stopped: _cancel(k)
    msg = f"تم إيقاف: {', '.join(stopped)}" if stopped else "لا يوجد نشر نشط"
    await event.edit(msg)


@client.on(events.NewMessage(outgoing=True, pattern=r"^\.ايقاف السبام$"))
async def stop_all_spam(event):
    count = len(_tasks)
    _cancel_all()
    await event.edit(f"تم إيقاف جميع العمليات ({count})" if count else "لا توجد عمليات نشطة")
