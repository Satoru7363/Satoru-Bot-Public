# ════════════════════════════════════════
#  Satoru — م4 + م20 + م23: المجموعة والحماية والتفليش
# ════════════════════════════════════════
import re, asyncio
from satoru import client
from telethon import events
from telethon.tl.functions.channels import EditBannedRequest, EditAdminRequest
from telethon.tl.types import ChatBannedRights, ChatAdminRights
from database import db


async def _resolve_user(event, username=None):
    reply = await event.get_reply_message()
    if reply:
        return reply.sender_id, reply.sender
    if username:
        try:
            e = await client.get_entity(username.lstrip("@"))
            return e.id, e
        except Exception:
            pass
    return None, None


# ══════════════════════════════════════
#  الكتم
# ══════════════════════════════════════

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.كتم ?(@?\S+)?$"))
async def mute_user(event):
    await event.delete()
    if not event.is_group:
        return await event.respond("هذا الأمر للمجموعات فقط")
    uid, user = await _resolve_user(event, event.pattern_match.group(1))
    if not uid:
        return await event.respond("حدد المستخدم بالرد أو بذكر اليوزرنيم")
    chat_id = str(event.chat_id)
    db.sadd(f"muted:{chat_id}", uid)
    name = getattr(user, "first_name", str(uid)) if user else str(uid)
    try:
        rights = ChatBannedRights(
            until_date=None, send_messages=True, send_media=True,
            send_stickers=True, send_gifs=True, send_games=True,
            send_inline=True, embed_links=True,
        )
        await client(EditBannedRequest(event.chat_id, uid, rights))
        await event.respond(f"تم كتم: `{name}`")
    except Exception:
        await event.respond(f"تم كتم (محلياً): `{name}`")


@client.on(events.NewMessage(outgoing=True, pattern=r"^\.الغاء الكتم ?(@?\S+)?$"))
async def unmute_user(event):
    await event.delete()
    uid, user = await _resolve_user(event, event.pattern_match.group(1))
    if not uid:
        return await event.respond("حدد المستخدم")
    chat_id = str(event.chat_id)
    db.srem(f"muted:{chat_id}", uid)
    name = getattr(user, "first_name", str(uid)) if user else str(uid)
    try:
        await client(EditBannedRequest(event.chat_id, uid, ChatBannedRights(until_date=None)))
        await event.respond(f"تم إلغاء الكتم: `{name}`")
    except Exception:
        await event.respond(f"تم إلغاء الكتم المحلي: `{name}`")


@client.on(events.NewMessage(outgoing=True, pattern=r"^\.(?:الكتم|مكتومين)$"))
async def list_muted(event):
    await event.delete()
    muted = db.smembers(f"muted:{event.chat_id}")
    if not muted:
        return await event.respond("لا يوجد مكتومون")
    await event.respond("**المكتومون:**\n" + "\n".join(f"  `{uid}`" for uid in muted))


@client.on(events.NewMessage(outgoing=True, pattern=r"^\.مسح الكتم$"))
async def clear_muted(event):
    await event.delete()
    db.sdelete(f"muted:{event.chat_id}")
    await event.respond("تم مسح قائمة الكتم")


# ══════════════════════════════════════
#  التثبيت
# ══════════════════════════════════════

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.تثبيت$"))
async def pin_msg(event):
    await event.delete()
    reply = await event.get_reply_message()
    if not reply:
        return await event.respond("يجب الرد على الرسالة المراد تثبيتها")
    try:
        await client.pin_message(event.chat_id, reply.id, notify=True)
        await event.respond("تم تثبيت الرسالة")
    except Exception as e:
        await event.respond(str(e))


@client.on(events.NewMessage(outgoing=True, pattern=r"^\.الغاء التثبيت$"))
async def unpin_msg(event):
    await event.delete()
    reply = await event.get_reply_message()
    if not reply:
        return await event.respond("يجب الرد على الرسالة")
    try:
        await client.unpin_message(event.chat_id, reply.id)
        await event.respond("تم إلغاء التثبيت")
    except Exception as e:
        await event.respond(str(e))


# ══════════════════════════════════════
#  منع الكلمات
# ══════════════════════════════════════

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.منع (.+)$"))
async def ban_word(event):
    await event.delete()
    word = event.pattern_match.group(1).strip()
    db.sadd(f"banned_words:{event.chat_id}", word.lower())
    await event.respond(f"تم منع الكلمة: `{word}`")


@client.on(events.NewMessage(outgoing=True, pattern=r"^\.الغاء المنع (.+)$"))
async def unban_word(event):
    await event.delete()
    word = event.pattern_match.group(1).strip()
    db.srem(f"banned_words:{event.chat_id}", word.lower())
    await event.respond(f"تم إلغاء منع: `{word}`")


@client.on(events.NewMessage(outgoing=True, pattern=r"^\.قائمة المنع$"))
async def list_banned_words(event):
    await event.delete()
    words = db.smembers(f"banned_words:{event.chat_id}")
    if not words:
        return await event.respond("لا توجد كلمات ممنوعة")
    await event.respond("**الكلمات الممنوعة:**\n" + "\n".join(f"  `{w}`" for w in sorted(words)))


# ══════════════════════════════════════
#  معلومات المجموعة / العضو
# ══════════════════════════════════════

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.كيف الجروب$"))
async def group_info(event):
    await event.delete()
    try:
        chat = await client.get_entity(event.chat_id)
        parts = await client.get_participants(event.chat_id)
        text = (
            f"**معلومات المجموعة:**\n\n"
            f"  الاسم   :  `{chat.title}`\n"
            f"  المعرف  :  `{event.chat_id}`\n"
            f"  الأعضاء :  `{len(parts)}`\n"
        )
        if getattr(chat, "username", None):
            text += f"  اليوزر  :  @{chat.username}\n"
        await event.respond(text)
    except Exception as e:
        await event.respond(str(e))


@client.on(events.NewMessage(outgoing=True, pattern=r"^\.عضو ?(@?\S+)?$"))
async def member_info(event):
    await event.delete()
    m = event.pattern_match.group(1)
    uid, user = await _resolve_user(event, m)
    if not user:
        try:
            me = await client.get_me()
            user, uid = me, me.id
        except Exception:
            return await event.respond("حدد المستخدم")
    name  = f"{getattr(user,'first_name','')} {getattr(user,'last_name','') or ''}".strip()
    uname = f"@{user.username}" if getattr(user, "username", None) else "لا يوجد"
    await event.respond(
        f"**معلومات العضو:**\n\n"
        f"  الاسم   :  `{name}`\n"
        f"  اليوزر  :  {uname}\n"
        f"  المعرف  :  `{uid}`\n"
        f"  بوت     :  {'نعم' if getattr(user,'bot',False) else 'لا'}\n"
    )


# ══════════════════════════════════════
#  حماية المجموعة — م20
# ══════════════════════════════════════

def _pk(chat_id, name):
    return f"protect:{chat_id}:{name}"


@client.on(events.NewMessage(outgoing=True, pattern=r"^\.ضد الروابط (تشغيل|إيقاف)$"))
async def anti_links(event):
    await event.delete()
    state = event.pattern_match.group(1) == "تشغيل"
    db.set(_pk(event.chat_id, "links"), state)
    await event.respond(f"{'تم تفعيل' if state else 'تم تعطيل'} الحماية ضد الروابط")


@client.on(events.NewMessage(outgoing=True, pattern=r"^\.ضد السبام (تشغيل|إيقاف)$"))
async def anti_spam(event):
    await event.delete()
    state = event.pattern_match.group(1) == "تشغيل"
    db.set(_pk(event.chat_id, "spam"), state)
    await event.respond(f"{'تم تفعيل' if state else 'تم تعطيل'} الحماية ضد السبام")


@client.on(events.NewMessage(outgoing=True, pattern=r"^\.ضد الستيكر (تشغيل|إيقاف)$"))
async def anti_sticker(event):
    await event.delete()
    state = event.pattern_match.group(1) == "تشغيل"
    db.set(_pk(event.chat_id, "stickers"), state)
    await event.respond(f"{'تم تفعيل' if state else 'تم تعطيل'} الحماية ضد الملصقات")


@client.on(events.NewMessage(outgoing=True, pattern=r"^\.ضد السب (تشغيل|إيقاف)$"))
async def anti_bad(event):
    await event.delete()
    state = event.pattern_match.group(1) == "تشغيل"
    db.set(_pk(event.chat_id, "badwords"), state)
    await event.respond(f"{'تم تفعيل' if state else 'تم تعطيل'} الحماية ضد السب")


@client.on(events.NewMessage(outgoing=True, pattern=r"^\.قائمة الحماية$"))
async def protection_list(event):
    await event.delete()
    cid = event.chat_id
    items = {
        "الروابط":  _pk(cid, "links"),
        "السبام":   _pk(cid, "spam"),
        "الملصقات": _pk(cid, "stickers"),
        "السب":     _pk(cid, "badwords"),
    }
    text = "**اعدادات الحماية:**\n\n"
    for label, key in items.items():
        state = "مفعّل" if db.get(key) else "معطّل"
        text += f"  {label}  :  {state}\n"
    await event.respond(text)


# ══════════════════════════════════════
#  التفليش — م23
# ══════════════════════════════════════

# ── .فلش @يوزر — معلومات شخص ────────────────────────────────────
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.فلش ?(@?\S+)?$"))
async def flash_user(event):
    await event.delete()
    m = event.pattern_match.group(1)
    uid, user = await _resolve_user(event, m)
    if not user:
        return await event.respond("حدد الشخص بالرد أو بذكر اليوزر")
    name  = f"{getattr(user,'first_name','')} {getattr(user,'last_name','') or ''}".strip()
    uname = f"@{user.username}" if getattr(user, "username", None) else "—"
    await event.respond(
        f"**تفليش:**\n\n"
        f"  الاسم   :  {name}\n"
        f"  اليوزر  :  {uname}\n"
        f"  الايدي  :  `{uid}`\n"
        f"  بوت     :  {'نعم' if getattr(user,'bot',False) else 'لا'}\n"
    )


# ── .تفليش — حظر جميع أعضاء المجموعة ─────────────────────────────
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.تفليش$"))
async def flash_group(event):
    """
    حظر جميع أعضاء المجموعة الحالية (يتطلب صلاحيات أدمن)
    استخدام هذا الأمر يحظر الجميع ما عدا المستخدم نفسه.
    """
    await event.delete()
    if not event.is_group:
        return await event.respond("هذا الأمر للمجموعات فقط")

    msg = await event.respond("جاري تفليش المجموعة...")
    me  = await client.get_me()

    banned_count = 0
    failed_count = 0

    try:
        participants = await client.get_participants(event.chat_id)
    except Exception as e:
        return await msg.edit(f"فشل جلب الأعضاء: {e}")

    rights = ChatBannedRights(until_date=None, view_messages=True)

    for p in participants:
        if p.id == me.id:
            continue
        if getattr(p, "is_creator", False) or getattr(p, "admin_rights", None):
            continue
        try:
            await client(EditBannedRequest(event.chat_id, p.id, rights))
            banned_count += 1
            await asyncio.sleep(0.3)
        except Exception:
            failed_count += 1

    await msg.edit(
        f"**تم التفليش**\n\n"
        f"  محظور   :  {banned_count}\n"
        f"  فشل     :  {failed_count}\n"
    )


# ══════════════════════════════════════
#  Watcher المجموعة
# ══════════════════════════════════════

BAD_WORDS_DEFAULT = ["كس", "عير", "خول", "زبي", "شرموط", "قحبه", "متناك"]
URL_PATTERN = re.compile(r"(https?://|www\.)[^\s]+|t\.me/[^\s]+", re.IGNORECASE)


@client.on(events.NewMessage(incoming=True, func=lambda e: e.is_group))
async def group_watcher(event):
    cid    = event.chat_id
    c_str  = str(cid)
    sender = event.sender_id
    text   = event.text or ""

    me = await client.get_me()
    if sender == me.id:
        return

    # مكتوم
    if db.sismember(f"muted:{c_str}", sender):
        try: await event.delete()
        except Exception: pass
        return

    # كلمات ممنوعة مخصصة
    banned = db.smembers(f"banned_words:{c_str}")
    if banned and text:
        tl = text.lower()
        if any(w in tl for w in banned):
            try: await event.delete()
            except Exception: pass
            return

    # حماية ضد السب
    if db.get(_pk(cid, "badwords")) and text:
        tl = text.lower()
        if any(bw in tl for bw in BAD_WORDS_DEFAULT):
            try: await event.delete()
            except Exception: pass
            return

    # حماية ضد الروابط
    if db.get(_pk(cid, "links")) and text:
        if URL_PATTERN.search(text):
            try: await event.delete()
            except Exception: pass
            return

    # حماية ضد الملصقات
    if db.get(_pk(cid, "stickers")) and event.sticker:
        try: await event.delete()
        except Exception: pass
        return
