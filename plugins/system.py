# ════════════════════════════════════════
#  Satoru — النظام والمعلومات
# ════════════════════════════════════════
import os, sys, time, asyncio
from io import StringIO
from satoru import client
from telethon import events
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.functions.photos import GetUserPhotosRequest
from database import db

START_TIME = time.time()


# ── .ping ─────────────────────────────────────────────────────────
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.ping$"))
async def ping(event):
    t0  = time.time()
    msg = await event.edit("...")
    ms  = round((time.time() - t0) * 1000, 2)
    up  = int(time.time() - START_TIME)
    h, r = divmod(up, 3600)
    m, s = divmod(r, 60)
    await msg.edit(
        f"**Satoru — متصل**\n\n"
        f"  السرعة         :  `{ms}ms`\n"
        f"  وقت التشغيل   :  `{h}h {m}m {s}s`"
    )


# ── .فحص ─────────────────────────────────────────────────────────
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.فحص$"))
async def check(event):
    up = int(time.time() - START_TIME)
    h, r = divmod(up, 3600)
    m, s = divmod(r, 60)
    await event.edit(
        f"**Satoru Userbot — يعمل**\n\n"
        f"  الإصدار       :  `v2.0`\n"
        f"  وقت التشغيل   :  `{h}h {m}m {s}s`\n"
        f"  Python        :  `{sys.version.split()[0]}`\n\n"
        f"اكتب `.الاوامر` لعرض القوائم"
    )


# ══════════════════════════════════════
#  بروفايل المستخدم
# ══════════════════════════════════════

async def _build_profile(user, chat_id=None, is_owner=False):
    try:
        full = await client(GetFullUserRequest(user.id))
        bio  = full.full_user.about or "—"
    except Exception:
        bio = "—"

    try:
        photos = await client(GetUserPhotosRequest(user_id=user.id, offset=0, max_id=0, limit=100))
        ph_count = len(photos.photos)
    except Exception:
        ph_count = 0

    name  = f"{user.first_name or ''} {user.last_name or ''}".strip() or "—"
    uname = f"@{user.username}" if getattr(user, "username", None) else "—"

    rank = "مالك" if is_owner else "مستخدم"
    if chat_id and not is_owner:
        try:
            p = await client.get_permissions(chat_id, user.id)
            if getattr(p, "is_creator", False):   rank = "مؤسس"
            elif getattr(p, "is_admin", False):    rank = "مشرف"
            else:                                  rank = "عضو"
        except Exception:
            pass

    return (
        f"𝖭𝖠𝖬𝖤  ▹  {name}\n"
        f"𝖴𝖲𝖤   ▹  {uname}\n"
        f"𝖲𝖳𝖠   ▹  {rank}\n"
        f"𝖨𝖣    ▹  `{user.id}`\n"
        f"𝖯𝗁𝗈𝗍𝗈 ▹  {ph_count} صورة\n"
        f"𝖡𝗂𝗈   ▹  {bio}"
    )


# ── .ايدي ─────────────────────────────────────────────────────────
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.ايدي$"))
async def show_my_id(event):
    await event.delete()
    me   = await client.get_me()
    text = await _build_profile(me, is_owner=True)
    tmp  = f"pfp_me_{me.id}.jpg"
    try:
        path = await client.download_profile_photo(me.id, file=tmp)
        if path and os.path.exists(path):
            await client.send_file(event.chat_id, path, caption=text)
            try: os.remove(path)
            except Exception: pass
            return
    except Exception:
        pass
    await event.respond(text)


# ── .كشف (بالرد) ─────────────────────────────────────────────────
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.كشف$"))
async def reveal_user(event):
    await event.delete()
    reply = await event.get_reply_message()
    if not reply:
        return await event.respond("يجب الرد على رسالة شخص")
    try:
        user = await client.get_entity(reply.sender_id)
    except Exception:
        return await event.respond("تعذر جلب المعلومات")

    text = await _build_profile(user, chat_id=event.chat_id)
    tmp  = f"pfp_user_{user.id}.jpg"
    try:
        path = await client.download_profile_photo(user.id, file=tmp)
        if path and os.path.exists(path):
            await client.send_file(event.chat_id, path, caption=text)
            try: os.remove(path)
            except Exception: pass
            return
    except Exception:
        pass
    await event.respond(text)


# ── .معلوماتي ────────────────────────────────────────────────────
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.معلوماتي$"))
async def my_info(event):
    await event.delete()
    me   = await client.get_me()
    text = await _build_profile(me, is_owner=True)
    await event.respond(text)


# ── .session ─────────────────────────────────────────────────────
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.session$"))
async def get_session(event):
    await event.delete()
    from telethon.sessions import StringSession
    sess = StringSession.save(client.session)
    await client.send_message("me", f"**Session String:**\n`{sess}`")
    await event.respond("تم إرسال الـ Session لـ Saved Messages")


# ── .eval ────────────────────────────────────────────────────────
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.eval (.+)$", func=lambda e: e.out))
async def eval_code(event):
    code = event.pattern_match.group(1)
    old  = sys.stdout
    sys.stdout = buf = StringIO()
    try:
        exec(compile(code, "<string>", "exec"), {"client": client, "event": event, "db": db})
        out = buf.getvalue() or "(no output)"
    except Exception as e:
        out = f"Error: {e}"
    finally:
        sys.stdout = old
    await event.edit(f"**Eval:**\n```\n{code}\n```\n**Output:**\n```\n{out[:900]}\n```")


# ── .bash ────────────────────────────────────────────────────────
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.bash (.+)$", func=lambda e: e.out))
async def bash_cmd(event):
    cmd = event.pattern_match.group(1)
    try:
        proc = await asyncio.create_subprocess_shell(
            cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        out1, out2 = await asyncio.wait_for(proc.communicate(), timeout=30)
        out = (out1.decode() or out2.decode() or "(no output)")[:900]
    except asyncio.TimeoutError:
        out = "Timeout (30s)"
    except Exception as e:
        out = str(e)
    await event.edit(f"**Bash:**\n```\n{cmd}\n```\n**Output:**\n```\n{out}\n```")


# ── .نصب ────────────────────────────────────────────────────────
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.نصب (.+)$"))
async def pip_install(event):
    await event.delete()
    pkgs = event.pattern_match.group(1).strip()
    msg  = await event.respond(f"جاري تثبيت: `{pkgs}`...")
    try:
        proc = await asyncio.create_subprocess_exec(
            sys.executable, "-m", "pip", "install", *pkgs.split(),
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        _, err = await asyncio.wait_for(proc.communicate(), timeout=120)
        if proc.returncode == 0:
            await msg.edit(f"تم تثبيت: `{pkgs}` بنجاح")
        else:
            await msg.edit(f"خطأ:\n```{err.decode()[:400]}```")
    except Exception as e:
        await msg.edit(str(e))


# ── .اعادة تشغيل ─────────────────────────────────────────────────
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.اعادة تشغيل$"))
async def restart_bot(event):
    await event.edit("جاري إعادة التشغيل...")
    await asyncio.sleep(1)
    os.execv(sys.executable, [sys.executable] + sys.argv)
