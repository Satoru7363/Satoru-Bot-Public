# ════════════════════════════════════════
#  Satoru — م25: الألعاب ووعد
# ════════════════════════════════════════
import random, asyncio
from satoru import client
from telethon import events
from database import db

# حالة الألعاب النشطة: {chat_id: game_data}
_games: dict = {}


# ══════════════════════════════════════
#  ألعاب بسيطة
# ══════════════════════════════════════

# ── .نرد ────────────────────────────────
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.نرد$"))
async def roll_dice(event):
    n     = random.randint(1, 6)
    faces = ["⚀", "⚁", "⚂", "⚃", "⚄", "⚅"]
    await event.edit(f"رميت النرد — **{faces[n-1]} ({n})**")


# ── .عملة ───────────────────────────────
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.عملة$"))
async def flip_coin(event):
    result = random.choice(["صورة", "كتابة"])
    await event.edit(f"رميت العملة — **{result}**")


# ── .عجلةالحظ ───────────────────────────
WHEEL = [
    "جائزة كبرى", "نجمة مضيئة", "حظ موفور",
    "هدية مفاجأة", "فوز ساحق", "لا شيء هذه المرة",
    "دور مجاني", "كنز مخفي", "محاولة أخرى",
]

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.عجلة الحظ$"))
async def spin_wheel(event):
    result = random.choice(WHEEL)
    await event.edit(f"**عجلة الحظ تدور...**\n\nالنتيجة: **{result}**")


# ── .عشوائيرقم MIN MAX ──────────────────
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.رقم عشوائي (\d+) (\d+)$"))
async def random_number(event):
    lo = int(event.pattern_match.group(1))
    hi = int(event.pattern_match.group(2))
    if lo > hi:
        lo, hi = hi, lo
    await event.edit(f"رقم عشوائي بين `{lo}` و `{hi}`: **{random.randint(lo, hi)}**")


# ══════════════════════════════════════
#  حجرة ورقة مقص
# ══════════════════════════════════════

RPS_WIN = {"حجر": "مقص", "ورقة": "حجر", "مقص": "ورقة"}
RPS_CHOICES = ["حجر", "ورقة", "مقص"]


@client.on(events.NewMessage(outgoing=True, pattern=r"^\.حجرة ورقة مقص$"))
async def rps_start(event):
    cid = event.chat_id
    _games[cid] = {"type": "rps", "waiting": True}
    await event.edit(
        "**حجرة ورقة مقص**\n\n"
        "اختر في رسالة جديدة:\n"
        "  `.حجر`    `.ورقة`    `.مقص`\n\n"
        "عندك 30 ثانية"
    )
    await asyncio.sleep(30)
    if _games.get(cid, {}).get("waiting"):
        _games.pop(cid, None)
        try: await client.send_message(cid, "انتهى الوقت — لم تختر!")
        except Exception: pass


@client.on(events.NewMessage(outgoing=True, pattern=r"^\.(حجر|ورقة|مقص)$"))
async def rps_play(event):
    cid = event.chat_id
    g   = _games.get(cid)
    if not g or g.get("type") != "rps" or not g.get("waiting"):
        return

    _games[cid]["waiting"] = False
    user_c = event.pattern_match.group(1)
    bot_c  = random.choice(RPS_CHOICES)

    if user_c == bot_c:
        result = "تعادل"
    elif RPS_WIN[user_c] == bot_c:
        result = "انت الفائز"
    else:
        result = "خسرت"

    _games.pop(cid, None)
    await event.edit(
        f"**النتيجة:**\n\n"
        f"  أنت   :  {user_c}\n"
        f"  أنا   :  {bot_c}\n\n"
        f"**{result}**"
    )


# ══════════════════════════════════════
#  خمّن الرقم
# ══════════════════════════════════════

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.خمن رقم$"))
async def guess_number_start(event):
    cid = event.chat_id
    n   = random.randint(1, 25)
    _games[cid] = {"type": "guess", "number": n, "tries": 7}
    await event.edit(
        "**خمّن الرقم**\n\n"
        "اخترت رقماً بين 1 و 25\n"
        "عندك 7 محاولات — اكتب `.خمن [رقم]`"
    )


@client.on(events.NewMessage(outgoing=True, pattern=r"^\.خمن (\d+)$"))
async def guess_number_try(event):
    cid = event.chat_id
    g   = _games.get(cid)
    if not g or g.get("type") != "guess":
        return

    guess  = int(event.pattern_match.group(1))
    target = g["number"]
    g["tries"] -= 1

    if guess == target:
        _games.pop(cid, None)
        return await event.edit(f"**صحيح!** الرقم كان **{target}**")

    if g["tries"] <= 0:
        _games.pop(cid, None)
        return await event.edit(f"**خسرت!** الرقم كان **{target}**")

    hint = "أكبر" if guess < target else "أصغر"
    await event.edit(
        f"الرقم **{hint}** من `{guess}`\n"
        f"متبقي: **{g['tries']}** محاولات"
    )


# ══════════════════════════════════════
#  المحيبس (لعبة عربية شهيرة)
# ══════════════════════════════════════

PLAYERS = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]


@client.on(events.NewMessage(outgoing=True, pattern=r"^\.محيبس$"))
async def muhaibes_start(event):
    cid = event.chat_id
    team = random.sample(PLAYERS, 5)
    hidden_idx = random.randint(0, 4)
    _games[cid] = {
        "type": "muhaibes",
        "team": team,
        "hidden": hidden_idx,
        "tries": 3,
    }
    await event.edit(
        "**لعبة المحيبس**\n\n"
        f"الفريق: {' — '.join(team)}\n\n"
        "المحبس بايد من هاي الايادي!\n"
        "عندك 3 محاولات — اكتب `.خاتم [رقم الايد]`"
    )


@client.on(events.NewMessage(outgoing=True, pattern=r"^\.خاتم (.+)$"))
async def muhaibes_guess(event):
    cid = event.chat_id
    g   = _games.get(cid)
    if not g or g.get("type") != "muhaibes":
        return

    guess  = event.pattern_match.group(1).strip()
    team   = g["team"]
    hidden = team[g["hidden"]]
    g["tries"] -= 1

    if guess == hidden:
        _games.pop(cid, None)
        return await event.edit(f"**صحيح!** الخاتم كان في **{hidden}**")

    if g["tries"] <= 0:
        _games.pop(cid, None)
        return await event.edit(f"**خسرت!** الخاتم كان في **{hidden}**")

    await event.edit(
        f"غلط — الخاتم مو في `{guess}`\n"
        f"متبقي: **{g['tries']}** محاولات\n"
        f"الفريق: {' — '.join(team)}"
    )


# ══════════════════════════════════════
#  لعبة كلمة وصاحبها
# ══════════════════════════════════════

WORD_GAME = [
    ("ما أسرع طائر في العالم؟", "الصقر الحر"),
    ("عاصمة اليابان؟", "طوكيو"),
    ("كم عدد أضلاع المثلث؟", "ثلاثة"),
    ("ما اللغة الأكثر انتشاراً في العالم؟", "الإنجليزية"),
    ("ما اسم أطول نهر في العالم؟", "النيل"),
    ("من أول إنسان مشى على القمر؟", "نيل أرمسترونج"),
    ("كم عدد دول العالم؟", "١٩٣"),
    ("ما أكبر كوكب في المجموعة الشمسية؟", "المشتري"),
]


@client.on(events.NewMessage(outgoing=True, pattern=r"^\.مسابقة$"))
async def word_quiz_start(event):
    cid = event.chat_id
    q, a = random.choice(WORD_GAME)
    _games[cid] = {"type": "quiz", "answer": a.lower(), "q": q}
    await event.edit(
        f"**سؤال:**\n\n{q}\n\n"
        f"اكتب إجابتك مباشرة — عندك 60 ثانية\n"
        f"للإلغاء: `.الغاء المسابقة`"
    )
    await asyncio.sleep(60)
    if _games.get(cid, {}).get("type") == "quiz":
        _games.pop(cid, None)
        try: await client.send_message(cid, f"انتهى الوقت — الإجابة الصحيحة: **{a}**")
        except Exception: pass


@client.on(events.NewMessage(outgoing=True, pattern=r"^\.الغاء المسابقة$"))
async def cancel_quiz(event):
    cid = event.chat_id
    if _games.pop(cid, None):
        await event.edit("تم إلغاء المسابقة")


@client.on(events.NewMessage(incoming=True))
async def quiz_listener(event):
    cid = event.chat_id
    g   = _games.get(cid)
    if not g or g.get("type") != "quiz":
        return
    if not event.text:
        return

    if event.text.strip().lower() == g["answer"]:
        _games.pop(cid, None)
        sender = await event.get_sender()
        name   = getattr(sender, "first_name", "شخص") if sender else "شخص"
        try:
            await event.reply(f"**صح!** {name} أجاب بشكل صحيح")
        except Exception:
            pass


# ══════════════════════════════════════
#  وعد
# ══════════════════════════════════════
