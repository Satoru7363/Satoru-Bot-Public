# ════════════════════════════════════════
#  Satoru — م14: الخطوط والترجمة
# ════════════════════════════════════════
import asyncio, json, urllib.request, urllib.parse
from satoru import client
from telethon import events
from utils import convert_font, tashkeel


# ══════════════════════════════════════
#  الخطوط
# ══════════════════════════════════════

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.بولد (.+)$"))
async def font_bold(event):
    await event.edit(convert_font(event.pattern_match.group(1), "bold"))

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.إيطالي (.+)$"))
async def font_italic(event):
    await event.edit(convert_font(event.pattern_match.group(1), "italic"))

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.سكريبت (.+)$"))
async def font_script(event):
    await event.edit(convert_font(event.pattern_match.group(1), "script"))

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.داابل (.+)$"))
async def font_double(event):
    await event.edit(convert_font(event.pattern_match.group(1), "double"))

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.مونو (.+)$"))
async def font_mono(event):
    await event.edit(convert_font(event.pattern_match.group(1), "mono"))

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.سمول (.+)$"))
async def font_small(event):
    await event.edit(convert_font(event.pattern_match.group(1), "smallcaps"))

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.ستريك (.+)$"))
async def font_strike(event):
    await event.edit(convert_font(event.pattern_match.group(1), "strike"))

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.وايد (.+)$"))
async def font_wide(event):
    await event.edit(convert_font(event.pattern_match.group(1), "wide"))

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.عكس (.+)$"))
async def font_reverse(event):
    await event.edit(event.pattern_match.group(1)[::-1])

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.فقاعة (.+)$"))
async def font_bubble(event):
    await event.edit(convert_font(event.pattern_match.group(1), "bubble"))


# ══════════════════════════════════════
#  الترجمة — Google Translate (غير رسمي)
# ══════════════════════════════════════

def _google_translate(text: str, target: str, source: str = "auto") -> str:
    """
    يستخدم واجهة Google Translate غير الرسمية — مجانية بدون مفتاح
    """
    try:
        url = (
            "https://translate.googleapis.com/translate_a/single"
            f"?client=gtx&sl={source}&tl={target}&dt=t&q={urllib.parse.quote(text)}"
        )
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            parts = data[0]
            return "".join(p[0] for p in parts if p and p[0])
    except Exception:
        return ""


async def _do_translate(event, target: str):
    await event.delete()
    reply = await event.get_reply_message()
    text  = ""

    if reply:
        text = reply.text or reply.caption or ""
    if not text:
        parts = event.raw_text.split(maxsplit=1)
        text  = parts[1] if len(parts) > 1 else ""
    if not text:
        return await event.respond("حدد النص بالرد أو ضعه بعد الأمر")

    msg    = await event.respond("جاري الترجمة...")
    result = await asyncio.get_event_loop().run_in_executor(
        None, _google_translate, text, target
    )
    if result:
        await msg.edit(result)
    else:
        await msg.edit("فشلت الترجمة — تحقق من اتصال الإنترنت")


# ── .ترجمar (بالرد أو بعد الأمر) ──────────────────────────────
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.ترجمar$"))
async def translate_ar(event):
    await _do_translate(event, "ar")

# ── .ترجمen ──────────────────────────────────────────────────────
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.ترجمen$"))
async def translate_en(event):
    await _do_translate(event, "en")

# ── .ترجم [كود] — أي لغة ─────────────────────────────────────────
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.ترجم ([a-zA-Z]{2,5})$"))
async def translate_lang(event):
    lang = event.pattern_match.group(1).lower()
    await _do_translate(event, lang)

# ── .ترجم — ترجمة لعدة لغات دفعة واحدة ─────────────────────────
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.ترجم$"))
async def translate_multi(event):
    await event.delete()
    reply = await event.get_reply_message()
    if not reply or not (reply.text or reply.caption):
        return await event.respond("يجب الرد على رسالة نصية")

    text = reply.text or reply.caption
    msg  = await event.respond("جاري الترجمة...")

    langs = {
        "en": "الإنجليزية",
        "ar": "العربية",
        "fr": "الفرنسية",
        "tr": "التركية",
        "ru": "الروسية",
    }

    lines = []
    for code, label in langs.items():
        t = await asyncio.get_event_loop().run_in_executor(
            None, _google_translate, text, code
        )
        if t:
            lines.append(f"**{label}:**\n{t}")

    await msg.edit("\n\n".join(lines) if lines else "فشلت الترجمة")


# ══════════════════════════════════════
#  التشكيل
# ══════════════════════════════════════

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.تشكيل (.+)$"))
async def add_tashkeel(event):
    text = event.pattern_match.group(1)
    await event.edit(tashkeel(text))
