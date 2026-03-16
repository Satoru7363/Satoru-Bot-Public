# ════════════════════════════════════════
#  Satoru — م6: المسح والنسخ
#  + حفظ الوسائط المؤقتة (ذاتية التدمير)
# ════════════════════════════════════════
import os
import asyncio
from datetime import datetime
from satoru import client
from telethon import events
from database import db


# ── .حذف (بالرد) أو .حذف عدد ──────────────────────────────────
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.حذف ?(\d+)?$"))
async def delete_msgs(event):
    await event.delete()
    reply = await event.get_reply_message()

    if reply and not event.pattern_match.group(1):
        try:
            await reply.delete()
        except Exception as e:
            await event.respond(f"⚠️ {e}")
        return

    count = int(event.pattern_match.group(1) or 1)
    if count > 200:
        count = 200

    msgs_to_del = []
    async for msg in client.iter_messages(event.chat_id, limit=count + 1):
        msgs_to_del.append(msg.id)

    try:
        await client.delete_messages(event.chat_id, msgs_to_del)
    except Exception as e:
        await event.respond(f"⚠️ {e}")


# ── .حذفي عدد — حذف رسائلي الأخيرة ────────────────────────────
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.حذفي (\d+)$"))
async def delete_my_msgs(event):
    await event.delete()
    count = min(int(event.pattern_match.group(1)), 200)
    me    = await client.get_me()
    ids   = []
    async for msg in client.iter_messages(event.chat_id, from_user=me.id, limit=count):
        ids.append(msg.id)
    if ids:
        await client.delete_messages(event.chat_id, ids)


# ── .نسخ (بالرد) ────────────────────────────────────────────────
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.نسخ$"))
async def copy_to_saved(event):
    await event.delete()
    reply = await event.get_reply_message()
    if not reply:
        return await event.respond("⚠️ يجب الرد على الرسالة المراد نسخها")

    try:
        if reply.media:
            await client.send_file("me", reply.media, caption=reply.text or "")
        else:
            await client.send_message("me", reply.text or "")
        await event.respond("**✓ تم نسخ الرسالة لـ Saved Messages**")
    except Exception as e:
        await event.respond(f"⚠️ {e}")


# ── .forward @هدف (بالرد) ───────────────────────────────────────
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.forward (@?\S+)$"))
async def forward_msg(event):
    await event.delete()
    target = event.pattern_match.group(1)
    reply  = await event.get_reply_message()
    if not reply:
        return await event.respond("⚠️ يجب الرد على الرسالة المراد توجيهها")

    try:
        entity = await client.get_entity(target)
        await client.forward_messages(entity, reply)
        await event.respond(f"**✓ تم توجيه الرسالة لـ** `{target}`")
    except Exception as e:
        await event.respond(f"⚠️ {e}")


# ── .مسح الكل عدد ────────────────────────────────────────────────
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.مسح الكل (\d+)$"))
async def delete_all(event):
    await event.delete()
    count = min(int(event.pattern_match.group(1)), 400)
    ids   = []
    async for msg in client.iter_messages(event.chat_id, limit=count):
        ids.append(msg.id)
    try:
        await client.delete_messages(event.chat_id, ids)
    except Exception as e:
        await event.respond(f"⚠️ {e}")


# ── .نسخ النص (بالرد) ────────────────────────────────────────────
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.نسخ النص$"))
async def copy_text(event):
    await event.delete()
    reply = await event.get_reply_message()
    if not reply or not reply.text:
        return await event.respond("⚠️ يجب الرد على رسالة نصية")
    await event.respond(f"`{reply.text}`")


# ═══════════════════════════════════════
#  الوسائط المؤقتة (ذاتية التدمير)
# ═══════════════════════════════════════

def _is_ttl(msg) -> bool:
    """التحقق إذا كانت الرسالة وسيطة ذاتية التدمير"""
    try:
        if msg.media and hasattr(msg.media, "ttl_seconds") and msg.media.ttl_seconds:
            return True
    except Exception:
        pass
    return False


async def _save_ttl_media(msg) -> bool:
    """
    يحفظ الوسيطة المؤقتة لـ Saved Messages بالتنسيق المطلوب،
    صامتاً تماماً دون أي إشعار في المحادثة الأصلية.
    """
    try:
        # بيانات المرسل
        sender = await msg.get_sender()
        if sender:
            first = getattr(sender, "first_name", "") or ""
            last  = getattr(sender, "last_name",  "") or ""
            name  = f"{first} {last}".strip() or "مجهول"
            uname = (
                f"@{sender.username}"
                if getattr(sender, "username", None)
                else f"`{sender.id}`"
            )
        else:
            name  = "مجهول"
            uname = "—"

        date_str = datetime.now().strftime("%Y-%m-%d")

        caption = (
            f"✦ : تم حفظ الوسائط المؤقتة ✓\n"
            f"                    ✦ : أسم المرسل: {name}\n"
            f"                    ✦ : معرف المستخدم: {uname}\n"
            f"                    ✦ : تاريخ الإرسال: {date_str}"
        )

        # تحميل الوسيطة
        file_path = await msg.download_media()
        if not file_path:
            return False

        # إرسال لـ Saved Messages
        await client.send_file("me", file_path, caption=caption)

        # حذف الملف المؤقت من القرص
        try:
            os.remove(file_path)
        except Exception:
            pass

        return True

    except Exception:
        return False


# ── .ذاتية (بالرد) — حفظ فوري صامت ────────────────────────────
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.ذاتية$"))
async def save_ttl_manual(event):
    """
    بالرد على وسيطة مؤقتة:
    - يحذف أمرك فوراً وبصمت
    - يحفظ الوسيطة لـ Saved Messages بالتنسيق المطلوب
    - يحاول حذف الرسالة الأصلية
    """
    reply = await event.get_reply_message()

    # حذف أمر .ذاتية صامت
    try:
        await event.delete()
    except Exception:
        pass

    if not reply or not reply.media:
        return

    await _save_ttl_media(reply)

    # حاول حذف رسالة الطرف الآخر (يعمل في الخاص فقط إذا كنت المرسل)
    try:
        await reply.delete()
    except Exception:
        pass


# ── .حفظ الذاتية — تشغيل الحفظ التلقائي ───────────────────────
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.(?:حفظ الذاتية|تشغيل الذاتية)$"))
async def enable_ttl_save(event):
    try:
        await event.delete()
    except Exception:
        pass
    db.set("auto_save_ttl", True)
    # إشعار يذهب لـ Saved Messages فقط
    await client.send_message("me", "**✓ تم تشغيل حفظ الوسائط المؤقتة تلقائياً**")


# ── .إيقاف الذاتية — إيقاف الحفظ التلقائي ─────────────────────
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.(?:إيقاف الذاتية|تعطيل الذاتية)$"))
async def disable_ttl_save(event):
    try:
        await event.delete()
    except Exception:
        pass
    db.set("auto_save_ttl", False)
    await client.send_message("me", "**✗ تم إيقاف حفظ الوسائط المؤقتة التلقائي**")


# ═══════════════════════════════════════
#  المستمع التلقائي — يشتغل في الخلفية
# ═══════════════════════════════════════
@client.on(events.NewMessage(incoming=True))
async def auto_ttl_watcher(event):
    """
    يراقب كل الرسائل الواردة بصمت تام.
    إذا كانت وسيطة ذاتية التدمير والحفظ مفعّل → يحفظها فوراً.
    """
    if not db.get("auto_save_ttl"):
        return

    if not event.media:
        return

    if not _is_ttl(event.message):
        return

    await _save_ttl_media(event.message)


# ════════════════════════════════════════
# Satoru — م7: التخزين الذكي (نسخة التحويل)
# بدون أي تحميل على الجهاز — تحويل مباشر
# ════════════════════════════════════════

import os
from datetime import datetime
from satoru import client
from telethon import events
from telethon.tl.functions.channels import CreateChannelRequest
from telethon.tl.types import (
    MessageMediaPhoto,
    MessageMediaDocument,
    DocumentAttributeAnimated,
    DocumentAttributeVideo,
)
from database import db

STORAGE_TITLE = "🗄 Satoru | المخزن"


# ══ دوال مساعدة ══════════════════════════════════════════════


async def _get_or_create_storage() -> int:
    saved = db.get("storage_group_id")
    if saved:
        try:
            await client.get_entity(int(saved))
            return int(saved)
        except Exception:
            pass

    result = await client(CreateChannelRequest(
        title=STORAGE_TITLE,
        about="• مخزن Satoru — تاكات | صور | فيديو | GIF",
        megagroup=True,
    ))
    gid = result.chats[0].id
    db.set("storage_group_id", gid)
    return gid


def _msg_link(chat, msg_id: int) -> str:
    try:
        username = getattr(chat, "username", None)
        if username:
            return f"https://t.me/{username}/{msg_id}"
        raw = str(chat.id).lstrip("-")
        if raw.startswith("100"):
            raw = raw[3:]
        return f"https://t.me/c/{raw}/{msg_id}"
    except Exception:
        return ""


def _detect_media_type(msg) -> str | None:
    if not msg.media:
        return None

    ttl = getattr(msg.media, "ttl_seconds", None)
    if ttl:
        return "ذاتية"

    if isinstance(msg.media, MessageMediaPhoto):
        return "صورة"

    if isinstance(msg.media, MessageMediaDocument):
        doc   = msg.media.document
        mime  = getattr(doc, "mime_type", "")
        attrs = getattr(doc, "attributes", [])

        if any(isinstance(a, DocumentAttributeAnimated) for a in attrs):
            return "متحرك"
        if "video" in mime or any(isinstance(a, DocumentAttributeVideo) for a in attrs):
            return "فيديو"
        if "image" in mime:
            return "صورة"

    return None


async def _sender_info(msg):
    try:
        sender = await msg.get_sender()
        if sender:
            first = getattr(sender, "first_name", "") or ""
            last  = getattr(sender, "last_name",  "") or ""
            name  = f"{first} {last}".strip() or "مجهول"
            uname = (
                f"@{sender.username}"
                if getattr(sender, "username", None)
                else f"ID:{sender.id}"
            )
            return name, uname
    except Exception:
        pass
    return "مجهول", "—"


async def _chat_name(msg) -> str:
    try:
        chat = await msg.get_chat()
        return (
            getattr(chat, "title",      None)
            or getattr(chat, "first_name", None)
            or "خاص"
        )
    except Exception:
        return "خاص"


# ══ بناء الكابشن ══════════════════════════════════════════════

async def _tag_caption(event) -> str:
    msg        = event.message
    name, _    = await _sender_info(msg)
    cname      = await _chat_name(msg)
    text       = (msg.text or msg.caption or "—").strip()
    chat       = await msg.get_chat()
    link       = _msg_link(chat, msg.id)
    link_part  = f"[اضغط هنا]({link})" if link else "—"

    return (
        f"**#التــاكــات**\n"
        f"⌔┊الكــروب : {cname}\n"
        f"⌔┊المـرسـل : {name}\n"
        f"⌔┊الرســالـه : {text}\n\n"
        f"⌔┊رابـط الرسـاله : {link_part}"
    )


async def _media_caption(event, mtype: str) -> str:
    msg        = event.message
    name, uid  = await _sender_info(msg)
    cname      = await _chat_name(msg)
    date_str   = datetime.now().strftime("%Y-%m-%d %H:%M")

    tag_map = {
        "صورة":   "#الصـــور",
        "فيديو":  "#الفيـديو",
        "متحرك":  "#المتحـركـة",
        "ذاتية":  "#ذاتيـة_التدمير ⏳",
    }
    hashtag = tag_map.get(mtype, "#وسـائط")

    return (
        f"**{hashtag}**\n"
        f"⌔┊المجموعة : {cname}\n"
        f"⌔┊المـرسـل : {name}\n"
        f"⌔┊المعـرف  : {uid}\n"
        f"⌔┊التـاريـخ : {date_str}"
    )


# ══ دالة التخزين — تحويل مباشر بدون تحميل ════════════════════

async def _store(event, caption: str, mtype: str | None = None):
    """
    التاكات     → نص فقط (أو تحويل إن فيها وسيطة)
    وسائط عادية → forward_messages مباشرة ثم رسالة الكابشن
    ذاتية       → لا يمكن تحويلها → نحفظ الكابشن فقط نصاً
    """
    gid = db.get("storage_group_id")
    if not gid:
        return

    try:
        storage = await client.get_entity(int(gid))
    except Exception:
        return

    msg = event.message

    # ── ذاتية التدمير: تحويل ممنوع من تيليجرام → نص فقط ──
    if mtype == "ذاتية":
        await client.send_message(
            storage, caption,
            parse_mode="md", link_preview=False
        )
        return

    # ── وسيطة عادية → تحويل مباشر + كابشن ──────────────────
    if msg.media:
        try:
            await client.forward_messages(storage, msg)
        except Exception:
            pass
        await client.send_message(
            storage, caption,
            parse_mode="md", link_preview=False
        )
        return

    # ── نص فقط (تاك بدون وسيطة) ─────────────────────────────
    await client.send_message(
        storage, caption,
        parse_mode="md", link_preview=False
    )


# ══ أوامر التشغيل / الإيقاف ══════════════════════════════════

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.تفعيل التخزين$"))
async def enable_storage(event):
    try:
        await event.delete()
    except Exception:
        pass
    db.set("auto_storage", True)
    gid   = await _get_or_create_storage()
    group = await client.get_entity(gid)
    title = getattr(group, "title", "المجموعة")
    await client.send_message(
        "me",
        f"✓ تم تفعيل التخزين\n📁 المجموعة : **{title}**"
    )


@client.on(events.NewMessage(outgoing=True, pattern=r"^\.تعطيل التخزين$"))
async def disable_storage(event):
    try:
        await event.delete()
    except Exception:
        pass
    db.set("auto_storage", False)
    await client.send_message("me", "✗ تم تعطيل التخزين التلقائي")


# ══ المستمع التلقائي ══════════════════════════════════════════

@client.on(events.NewMessage(incoming=True))
async def auto_storage_watcher(event):
    if not db.get("auto_storage"):
        return

    msg = event.message
    me  = await client.get_me()

    # ── تحديد نوع المحادثة ───────────────────────────────────
    is_private = event.is_private   # خاص
    is_group   = event.is_group or event.is_channel  # مجموعة أو قناة

    # ── مجموعة: فقط التاكات ─────────────────────────────────
    if is_group:
        is_tag = bool(
            msg.mentioned
            or (
                msg.text
                and me.username
                and f"@{me.username}".lower() in msg.text.lower()
            )
        )
        if not is_tag:
            return  # ← مجموعة وما فيها تاك = تجاهل

        caption = await _tag_caption(event)
        await _store(event, caption, mtype=None)
        return

    # ── خاص: كل شيء ─────────────────────────────────────────
    if is_private:
        mtype = _detect_media_type(msg)

        if mtype:
            caption = await _media_caption(event, mtype)
            await _store(event, caption, mtype=mtype)
        elif msg.text:
            # رسالة نصية عادية في الخاص
            name, uid = await _sender_info(msg)
            date_str  = datetime.now().strftime("%Y-%m-%d %H:%M")
            caption   = (
                f"**#الخـاص 💬**\n"
                f"⌔┊المـرسـل : {name}\n"
                f"⌔┊المعـرف  : {uid}\n"
                f"⌔┊الرسـالة : {msg.text}\n"
                f"⌔┊التـاريـخ : {date_str}"
            )
            await _store(event, caption, mtype=None)