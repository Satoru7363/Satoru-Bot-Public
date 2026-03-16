# ════════════════════════════════════════
#  Satoru — م5: الخاص والردود التلقائية
# ════════════════════════════════════════
import asyncio
from satoru import client
from telethon import events
from database import db
from config import OWNER_ID


def _owner_id():
    return db.get("owner_id", OWNER_ID)


# ══════════════════════════════════════
#  تشغيل / تعطيل الرد التلقائي
# ══════════════════════════════════════

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.تشغيل الرد$"))
async def enable_autoreply(event):
    await event.delete()
    db.set("autoreply:enabled", True)
    await event.respond("تم تشغيل الرد التلقائي")


@client.on(events.NewMessage(outgoing=True, pattern=r"^\.تعطيل الرد$"))
async def disable_autoreply(event):
    await event.delete()
    db.set("autoreply:enabled", False)
    await event.respond("تم تعطيل الرد التلقائي")


# ── نص الرد التلقائي ─────────────────────────────────────────────
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.نص الرد (.+)$"))
async def set_autoreply_text(event):
    await event.delete()
    text = event.pattern_match.group(1)
    db.set("autoreply:text", text)
    await event.respond(f"تم تعيين نص الرد:\n{text}")


# ══════════════════════════════════════
#  الردود المخصصة
# ══════════════════════════════════════

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.الرد (.+)$"))
async def add_custom_reply(event):
    await event.delete()
    trigger   = event.pattern_match.group(1).strip()
    reply_msg = await event.get_reply_message()
    if not reply_msg:
        return await event.respond("يجب الرد على الرسالة التي ستُرسل كرد تلقائي")
    db.set(f"custom_reply:{trigger}", {"text": reply_msg.text or ""})
    db.sadd("custom_replies", trigger)
    await event.respond(f"تم حفظ الرد عند كتابة: `{trigger}`")


@client.on(events.NewMessage(outgoing=True, pattern=r"^\.احذف الرد (.+)$"))
async def delete_custom_reply(event):
    await event.delete()
    trigger = event.pattern_match.group(1).strip()
    if db.exists(f"custom_reply:{trigger}"):
        db.delete(f"custom_reply:{trigger}")
        db.srem("custom_replies", trigger)
        await event.respond(f"تم حذف الرد: `{trigger}`")
    else:
        await event.respond(f"لا يوجد رد بالاسم: `{trigger}`")


@client.on(events.NewMessage(outgoing=True, pattern=r"^\.ردودي$"))
async def list_replies(event):
    await event.delete()
    replies = db.smembers("custom_replies")
    if not replies:
        return await event.respond("لا توجد ردود مخصصة")
    text = "**ردودي:**\n\n"
    for i, r in enumerate(sorted(replies), 1):
        text += f"  `{i}.`  {r}\n"
    await event.respond(text)


@client.on(events.NewMessage(outgoing=True, pattern=r"^\.مسح الردود$"))
async def clear_all_replies(event):
    await event.delete()
    for r in list(db.smembers("custom_replies")):
        db.delete(f"custom_reply:{r}")
    db.sdelete("custom_replies")
    await event.respond("تم مسح جميع الردود المخصصة")


# ══════════════════════════════════════
#  السماح / الرفض
# ══════════════════════════════════════

async def _get_uid(event, username=None):
    """استخراج معرف المستخدم من الرد أو اليوزرنيم أو المحادثة الحالية"""
    # من الرد
    reply = await event.get_reply_message()
    if reply:
        return reply.sender_id

    # من اليوزرنيم
    if username:
        try:
            entity = await client.get_entity(username.lstrip("@"))
            return entity.id
        except Exception:
            pass

    # من المحادثة الخاصة الحالية
    if event.is_private:
        return event.chat_id

    return None


@client.on(events.NewMessage(outgoing=True, pattern=r"^\.سماح ?(@?\S+)?$"))
async def allow_user(event):
    await event.delete()
    uid = await _get_uid(event, event.pattern_match.group(1))
    if uid:
        db.sadd("allowed_users", uid)
        db.srem("denied_users", uid)
        await event.respond(f"تم السماح للمستخدم `{uid}`")
    else:
        await event.respond("حدد الشخص بالرد أو بذكر اليوزر")


@client.on(events.NewMessage(outgoing=True, pattern=r"^\.رفض ?(@?\S+)?$"))
async def deny_user(event):
    """رفض رسائل شخص — يعمل بالرد أو بذكر اليوزرنيم أو في خاصه مباشرة"""
    await event.delete()
    uid = await _get_uid(event, event.pattern_match.group(1))
    if uid:
        db.sadd("denied_users", uid)
        db.srem("allowed_users", uid)
        await event.respond(f"تم رفض رسائل المستخدم `{uid}`")
    else:
        await event.respond("حدد الشخص بالرد أو بذكر اليوزر أو استخدم الأمر في خاصه")


# ══════════════════════════════════════
#  التقييد في الخاص
# ══════════════════════════════════════

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.تقييد ?(@?\S+)?$"))
async def restrict_private(event):
    await event.delete()
    uid = await _get_uid(event, event.pattern_match.group(1))
    if uid:
        db.sadd("pm_muted", uid)
        await event.respond(f"تم تقييد المستخدم في الخاص `{uid}`")
    else:
        await event.respond("حدد الشخص")


@client.on(events.NewMessage(outgoing=True, pattern=r"^\.الغاء تقييد الخاص ?(@?\S+)?$"))
async def unrestrict_private(event):
    await event.delete()
    uid = await _get_uid(event, event.pattern_match.group(1))
    if uid:
        db.srem("pm_muted", uid)
        await event.respond(f"تم إلغاء التقييد `{uid}`")
    else:
        await event.respond("حدد الشخص")

# ══════════════════════════════════════
#  التحذيرات والهمسة
# ══════════════════════════════════════

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.التحذيرات (\d+)$"))
async def set_warn_count(event):
    await event.delete()
    n = int(event.pattern_match.group(1))
    db.set("pm_warn_limit", n)
    await event.respond(f"تم تعيين عدد التحذيرات: `{n}`")


@client.on(events.NewMessage(outgoing=True, pattern=r"^\.اهمس (.+) (@\S+)$"))
async def whisper(event):
    await event.delete()
    text, username = event.pattern_match.group(1), event.pattern_match.group(2)
    try:
        entity = await client.get_entity(username)
        await client.send_message(entity, f"همسة: {text}")
        await event.respond(f"تم إرسال الهمسة لـ {username}")
    except Exception as e:
        await event.respond(str(e))


# ══════════════════════════════════════
#  مستمع الرد التلقائي
# ══════════════════════════════════════

@client.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
async def auto_reply_listener(event):
    owner     = _owner_id()
    sender_id = event.sender_id

    if sender_id == owner:
        return

    # إذا كان المستخدم مسموحًا له
    if db.sismember("allowed_users", sender_id):
        pass  # الرد التلقائي ممكن

    # إذا كان المستخدم مقيدًا في الخاص، احذف الرسالة
    elif db.sismember("pm_muted", sender_id):
        try:
            await event.delete()
        except:
            pass
        return

    # إذا كان المستخدم مرفوضًا، احذف الرسالة
    elif db.sismember("denied_users", sender_id):
        try:
            await event.delete()
        except:
            pass
        return

    # الرد التلقائي العام
    if db.get("autoreply:enabled"):
        msg_text = db.get("autoreply:text", "")
        if msg_text:
            await asyncio.sleep(0.5)
            await event.respond(msg_text)

    # الردود المخصصة
    if event.text:
        for trigger in db.smembers("custom_replies"):
            if trigger.lower() in event.text.lower():
                reply_data = db.get(f"custom_reply:{trigger}")
                if reply_data and reply_data.get("text"):
                    await asyncio.sleep(0.5)
                    await event.respond(reply_data["text"])
                break
