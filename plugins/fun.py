# ════════════════════════════════════════
#  Satoru — م9: التسلية  |  م10: التقليد
# ════════════════════════════════════════
import random, asyncio
from satoru import client
from telethon import events
from database import db


# ══════════════════════════════════════
#  م9 — التسلية الحقيقية
# ══════════════════════════════════════

JOKES = [
    "واحد قال لصاحبه: وش رأيك بالزواج؟\nقال: أحسن من الفراغ... والفراغ أحسن منه!",
    "واحد سأل الطبيب: كل ما آكل أتوجع!\nالطبيب: لا تأكل.\nواحد: وكل ما ما آكل أتوجع!\nالطبيب: لا تتوجع.",
    "واحد يبحث عن شغل. قالوا له: عندنا وظيفة تبدأ الساعة 4 الفجر.\nقال: ما يهم، أصلاً ما أنام قبلها.",
    "مدرس سأل الطالب: ما الفرق بين الجهل والكسل؟\nالطالب: لا أعرف ولا أريد أعرف.",
    "واحد اشترى بيتاً فخماً ثم اتصل بصاحبه يبكي.\nقال: وش صار؟\nقال: ما لقيت بيتي، العقد ما فيه عنوان.",
    "طفل سأل أباه: أبوي وش يعني متفائل؟\nقال: يعني تنتظر اللي ما راح يجي وتبتسم.",
    "واحد دخل مطعم قال: أعطني شيء خفيف.\nالنادل جاب الفاتورة.",
    "واحد قال لطبيبه: نسيت كل شيء.\nالطبيب: منذ متى؟\nقال: منذ متى وش؟",
]

FACTS = [
    "أكتوبوس يملك ثلاثة قلوب وتسعة أدمغة.",
    "النمل يستطيع حمل ما يعادل خمسين ضعف وزنه.",
    "العسل لا يفسد أبداً — عُثر على عسل عمره 3000 سنة في المقابر المصرية.",
    "القلب يضخ ما يكفي لملء شاحنة صهريج في السنة الواحدة.",
    "المحيط الهادئ وحده أكبر من مجموع مساحة كل اليابسة على الأرض.",
    "الفيل الوحيد الذي لا يستطيع القفز بين الثدييات الكبيرة.",
    "الأخطبوط يمكنه تغيير لونه وشكله في أجزاء من الثانية.",
    "الثعلب يمشي على رؤوس أصابعه لكي يصدر صوتاً أقل.",
]

WOULD_YOU = [
    ("تسافر إلى المريخ وحدك لمدة سنة", "تبقى في البيت بدون نت لمدة شهر"),
    ("تعرف تاريخ وفاتك", "تعرف سبب وفاتك فقط"),
    ("تطير بدون أجنحة", "تسبح تحت الماء بلا حاجة للهواء"),
    ("تتكلم مع الحيوانات", "تفهم كل لغة بشرية"),
    ("ترجع للماضي مرة واحدة", "تسافر للمستقبل مرة واحدة"),
]


# ── .نكتة ────────────────────────────────────────────────────────
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.نكتة$"))
async def random_joke(event):
    await event.edit(random.choice(JOKES))


# ── .معلومة ──────────────────────────────────────────────────────
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.معلومة$"))
async def random_fact(event):
    await event.edit(f"**معلومة:**\n\n{random.choice(FACTS)}")


# ── .ولاتولا ─────────────────────────────────────────────────────
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.ولاتولا$"))
async def would_you_rather(event):
    a, b = random.choice(WOULD_YOU)
    await event.edit(
        f"**ولا تولا؟**\n\n"
        f"  1️  {a}\n\n"
        f"  2️  {b}"
    )


# ── .عشوائي ──────────────────────────────────────────────────────
QUOTES = [
    "الحياة قصيرة — لا تضيعها في انتظار الإذن.",
    "النجاح ليس نهاية الطريق، والفشل ليس نهاية العالم.",
    "كل يوم فرصة جديدة — استغلها قبل أن تنتهي.",
    "الشخص الذكي يتعلم من أخطائه، الأذكى يتعلم من أخطاء غيره.",
    "الصمت أقوى رد على من لا يستحق الكلام.",
    "لا تشرح نفسك لأحد — من أحبك فهمك، ومن كرهك لن يصدقك.",
]

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.عشوائي$"))
async def random_quote(event):
    await event.edit(random.choice(QUOTES))


# ── .سر + نص (تشفير مضحك) ───────────────────────────────────────
_CIPHER = {
    "أ": "ي", "ب": "ه", "ت": "ن", "ث": "م", "ج": "ل", "ح": "ك",
    "خ": "ق", "د": "ف", "ذ": "غ", "ر": "ع", "ز": "ظ", "س": "ط",
    "ش": "ض", "ص": "ص", "ض": "ش", "ط": "س", "ظ": "ز", "ع": "ر",
    "غ": "ذ", "ف": "د", "ق": "خ", "ك": "ح", "ل": "ج", "م": "ث",
    "ن": "ت", "ه": "ب", "و": "ا", "ي": "أ", "ا": "و",
}

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.سر (.+)$"))
async def secret_text(event):
    text = event.pattern_match.group(1)
    await event.edit("".join(_CIPHER.get(c, c) for c in text))


# ── .عكس + نص ───────────────────────────────────────────────────
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.عكس النص (.+)$"))
async def fun_reverse(event):
    await event.edit(event.pattern_match.group(1)[::-1])


# ── .حجم + نص ────────────────────────────────────────────────────
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.حجم (.+)$"))
async def text_size(event):
    text  = event.pattern_match.group(1)
    words = len(text.split())
    chars = len(text)
    await event.edit(f"**حجم النص:**\n\n  الأحرف   :  `{chars}`\n  الكلمات  :  `{words}`")


# ── .هجوم @يوزر + رسالة ──────────────────────────────────────────
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.هجوم (@\S+) (.+)$"))
async def spam_user(event):
    await event.delete()
    target, text = event.pattern_match.group(1), event.pattern_match.group(2)
    try:
        entity = await client.get_entity(target)
        for _ in range(5):
            await client.send_message(entity, text)
            await asyncio.sleep(0.8)
    except Exception as e:
        await event.respond(str(e))


# ── .لهجةخليجي + نص ──────────────────────────────────────────────
_KG = {
    "أنا": "أنا وايد", "ماذا": "وش", "كيف": "كيف",
    "الآن": "الحين", "لا": "لا والله", "نعم": "إيه",
    "ثم": "بعدين", "لماذا": "ليش", "أين": "وين",
    "جميل": "حلو", "سيئ": "ما يجيب خير",
}

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.لهجة خليجي (.+)$"))
async def dialect_gulf(event):
    text = event.pattern_match.group(1)
    for k, v in _KG.items():
        text = text.replace(k, v)
    await event.edit(text)


# ── .لهجةمصري + نص ───────────────────────────────────────────────
_EG = {
    "أنا": "أنا بس", "ماذا": "إيه ده", "كيف": "إزيك",
    "الآن": "دلوقتي", "لا": "لأ", "نعم": "أيوا",
    "أين": "فين", "جميل": "حلو أوي", "سيئ": "وحش أوي",
    "لماذا": "ليه", "متى": "إمتى",
}

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.لهجة مصري (.+)$"))
async def dialect_egypt(event):
    text = event.pattern_match.group(1)
    for k, v in _EG.items():
        text = text.replace(k, v)
    await event.edit(text)


# ══════════════════════════════════════
#  م10 — التقليد التلقائي
# ══════════════════════════════════════

# تخزين حالة التقليد: {chat_id: {uid: int, reverse: bool}}
_mimic_state: dict = {}


# ── .تقليد (بالرد) — تقليد شخص تلقائياً ────────────────────────
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.تقليد$"))
async def start_mimic(event):
    await event.delete()
    reply = await event.get_reply_message()
    if not reply:
        return await event.respond("يجب الرد على رسالة الشخص المراد تقليده")

    cid = event.chat_id
    uid = reply.sender_id
    _mimic_state[cid] = {"uid": uid, "reverse": False}

    sender = await reply.get_sender()
    name = getattr(sender, "first_name", str(uid)) if sender else str(uid)
    await event.respond(
        f"**تم تفعيل التقليد**\n\n"
        f"  الهدف  :  {name}\n\n"
        f"سيتم تقليد كل رسائله في هذه المحادثة\n"
        f"للإيقاف: `.ايقاف التقليد`"
    )


# ── .تقليدعكسي (بالرد) ───────────────────────────────────────────
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.تقليد عكسي$"))
async def start_mimic_reverse(event):
    await event.delete()
    reply = await event.get_reply_message()
    if not reply:
        return await event.respond("يجب الرد على رسالة الشخص المراد تقليده")

    cid = event.chat_id
    uid = reply.sender_id
    _mimic_state[cid] = {"uid": uid, "reverse": True}

    sender = await reply.get_sender()
    name = getattr(sender, "first_name", str(uid)) if sender else str(uid)
    await event.respond(f"تم تفعيل التقليد المعكوس لـ {name}")


# ── .تقليدكل — تقليد الجميع في المحادثة ─────────────────────────
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.تقليد الكل$"))
async def start_mimic_all(event):
    await event.delete()
    cid = event.chat_id
    _mimic_state[cid] = {"uid": "all", "reverse": False}
    await event.respond(
        "**تقليد الجميع مفعّل**\n\n"
        "سيتم تقليد كل رسالة في هذه المحادثة\n"
        "للإيقاف: `.ايقاف التقليد`"
    )


# ── .ايقافتقليد ──────────────────────────────────────────────────
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.ايقاف التقليد$"))
async def stop_mimic(event):
    await event.delete()
    cid = event.chat_id
    if cid in _mimic_state:
        del _mimic_state[cid]
        await event.respond("تم إيقاف التقليد")
    else:
        await event.respond("لا يوجد تقليد نشط في هذه المحادثة")


# ── مستمع التقليد التلقائي ───────────────────────────────────────
@client.on(events.NewMessage(incoming=True))
async def mimic_listener(event):
    cid   = event.chat_id
    state = _mimic_state.get(cid)
    if not state:
        return

    sender = event.sender_id
    me     = await client.get_me()
    if sender == me.id:
        return

    # تحقق من الهدف
    if state["uid"] != "all" and sender != state["uid"]:
        return

    text = event.text or ""
    if not text and not event.media:
        return

    # تطبيق العكس إذا مطلوب
    if state.get("reverse") and text:
        text = text[::-1]

    try:
        if event.media and not text:
            await client.send_file(cid, event.media)
        elif text:
            await client.send_message(cid, text)
    except Exception:
        pass


# ── .قلد (بالرد) — تقليد رسالة واحدة عشوائياً ──────────────────
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.قلد$"))
async def mimic_once(event):
    await event.delete()
    reply = await event.get_reply_message()
    if not reply or not reply.text:
        return await event.respond("يجب الرد على رسالة نصية")
    words = reply.text.split()
    random.shuffle(words)
    await event.respond(" ".join(words))
