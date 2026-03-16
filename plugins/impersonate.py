# ════════════════════════════════════════
#  Satoru — م8: الانتحال والإرسال
# ════════════════════════════════════════
import os, asyncio
from satoru import client
from telethon import events
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.functions.photos import UploadProfilePhotoRequest, DeletePhotosRequest, GetUserPhotosRequest
from telethon.tl.functions.users import GetFullUserRequest
from database import db

TEMP_DIR = "temp_imp"
os.makedirs(TEMP_DIR, exist_ok=True)


# ══════════════════════════════════════
#  انتحال الهوية
# ══════════════════════════════════════

# ── .انتحال (بالرد أو في خاص شخص) ──────────────────────────────
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.انتحال$"))
async def impersonate_user(event):
    await event.delete()

    # تحديد الهدف
    target = None
    reply  = await event.get_reply_message()

    if reply:
        try:
            target = await client.get_entity(reply.sender_id)
        except Exception:
            pass
    elif event.is_private:
        try:
            target = await client.get_entity(event.chat_id)
        except Exception:
            pass

    if not target:
        return await event.respond("يجب الرد على رسالة شخص أو استخدام الأمر في خاصه")

    # حفظ الحساب الأصلي قبل الانتحال
    me = await client.get_me()
    try:
        full_me = await client(GetFullUserRequest(me.id))
        orig_bio = full_me.full_user.about or ""
    except Exception:
        orig_bio = ""

    db.set("impersonate:orig", {
        "first_name": me.first_name or "",
        "last_name":  me.last_name  or "",
        "bio":        orig_bio,
    })

    # جلب بيانات الهدف
    try:
        full_t   = await client(GetFullUserRequest(target.id))
        tgt_bio  = full_t.full_user.about or ""
    except Exception:
        tgt_bio  = ""

    t_first = getattr(target, "first_name", "") or ""
    t_last  = getattr(target, "last_name",  "") or ""

    msg = await event.respond("جاري الانتحال...")

    # تغيير الاسم والبايو
    try:
        await client(UpdateProfileRequest(
            first_name=t_first,
            last_name=t_last,
            about=tgt_bio
        ))
    except Exception as e:
        return await msg.edit(f"فشل تغيير الملف: {e}")

    # تغيير الصورة
    try:
        photo_path = os.path.join(TEMP_DIR, f"imp_{target.id}.jpg")
        dl = await client.download_profile_photo(target.id, file=photo_path)
        if dl:
            uploaded = await client.upload_file(dl)
            await client(UploadProfilePhotoRequest(file=uploaded))
            try: os.remove(dl)
            except Exception: pass
    except Exception:
        pass  # الصورة اختيارية

    t_name = f"{t_first} {t_last}".strip()
    db.set("impersonate:active", True)
    await msg.edit(
        f"**تم الانتحال بنجاح**\n\n"
        f"  الهدف   :  {t_name}\n"
        f"  الايدي  :  `{target.id}`\n\n"
        f"للإلغاء اكتب `.اعادة`"
    )


# ── .اعادة — استعادة الحساب الأصلي ─────────────────────────────
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.اعادة$"))
async def restore_account(event):
    await event.delete()

    orig = db.get("impersonate:orig")
    if not orig:
        return await event.respond("لا يوجد انتحال نشط حالياً")

    msg = await event.respond("جاري استعادة حسابك...")

    # استعادة الاسم والبايو
    try:
        await client(UpdateProfileRequest(
            first_name=orig.get("first_name", ""),
            last_name=orig.get("last_name", ""),
            about=orig.get("bio", "")
        ))
    except Exception as e:
        return await msg.edit(f"فشل الاستعادة: {e}")

    # حذف صورة الانتحال واستعادة الأصلية
    try:
        photos = await client(GetUserPhotosRequest(
            user_id="me", offset=0, max_id=0, limit=1
        ))
        if photos.photos:
            await client(DeletePhotosRequest(id=photos.photos[:1]))
    except Exception:
        pass

    db.delete("impersonate:orig")
    db.set("impersonate:active", False)
    await msg.edit("**تمت استعادة حسابك الأصلي**")


# ══════════════════════════════════════
#  أوامر الإرسال
# ══════════════════════════════════════

# ── .ارسل @هدف + رسالة ─────────────────────────────────────────
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.ارسل (@\S+) (.+)$"))
async def send_to(event):
    await event.delete()
    target, text = event.pattern_match.group(1), event.pattern_match.group(2)
    try:
        entity = await client.get_entity(target)
        await client.send_message(entity, text)
        await event.respond(f"تم الإرسال لـ {target}")
    except Exception as e:
        await event.respond(str(e))


# ── .ارسلميديا @هدف (بالرد) ─────────────────────────────────────
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.ارسل ميديا (@\S+)$"))
async def forward_media(event):
    await event.delete()
    target = event.pattern_match.group(1)
    reply  = await event.get_reply_message()
    if not reply or not reply.media:
        return await event.respond("يجب الرد على وسيطة")
    try:
        entity = await client.get_entity(target)
        await client.send_file(entity, reply.media, caption=reply.text or "")
        await event.respond(f"تم إرسال الوسيطة لـ {target}")
    except Exception as e:
        await event.respond(str(e))


# ── .نشرواحد @هدف (بالرد) ──────────────────────────────────────
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.نشر واحد (@?\S+)$"))
async def send_once(event):
    await event.delete()
    target = event.pattern_match.group(1)
    reply  = await event.get_reply_message()
    if not reply:
        return await event.respond("يجب الرد على رسالة")
    try:
        entity = await client.get_entity(target)
        if reply.media:
            await client.send_file(entity, reply.media, caption=reply.text or "")
        else:
            await client.send_message(entity, reply.text)
        await event.respond(f"تم النشر لـ {target}")
    except Exception as e:
        await event.respond(str(e))


# ── .مجهول + رسالة ──────────────────────────────────────────────
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.مجهول (.+)$"))
async def anonymous_msg(event):
    await event.delete()
    text = event.pattern_match.group(1)
    await event.respond(f"_{text}_")
