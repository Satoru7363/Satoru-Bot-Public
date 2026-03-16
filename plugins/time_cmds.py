# ════════════════════════════════════════
#  Satoru — م3: الوقت والتاريخ
# ════════════════════════════════════════
import asyncio
from datetime import datetime, timedelta

try:
    import pytz
    TZ = pytz.timezone("Asia/Baghdad")
    def _now():
        return datetime.now(TZ)
except ImportError:
    from datetime import timezone
    def _now():
        return datetime.utcnow() + timedelta(hours=3)

from satoru import client
from telethon import events

DAYS_AR = {
    "Monday": "الاثنين", "Tuesday": "الثلاثاء", "Wednesday": "الأربعاء",
    "Thursday": "الخميس", "Friday": "الجمعة", "Saturday": "السبت", "Sunday": "الأحد"
}
MONTHS_AR = {
    1: "يناير", 2: "فبراير", 3: "مارس", 4: "أبريل",
    5: "مايو", 6: "يونيو", 7: "يوليو", 8: "أغسطس",
    9: "سبتمبر", 10: "أكتوبر", 11: "نوفمبر", 12: "ديسمبر"
}

try:
    from hijri_converter import Gregorian
    _HIJRI = True
except ImportError:
    _HIJRI = False


# ── .وقت ─────────────────────────────────────────────────────────
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.وقت$"))
async def show_time(event):
    now   = _now()
    clock = now.strftime("%I:%M:%S %p")
    day   = DAYS_AR.get(now.strftime("%A"), now.strftime("%A"))
    await event.respond(
        f"**الوقت الحالي**\n\n"
        f"  الساعة  :  `{clock}`\n"
        f"  اليوم   :  `{day}`\n"
        f"  التوقيت :  بغداد (UTC+3)"
    )


# ── .تاريخ ───────────────────────────────────────────────────────
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.تاريخ$"))
async def show_date(event):
    now  = _now()
    mili = f"{now.day} {MONTHS_AR[now.month]} {now.year}"

    if _HIJRI:
        try:
            g = Gregorian(now.year, now.month, now.day)
            h = g.to_hijri()
            hijri_str = f"{h.day}/{h.month}/{h.year} هـ"
        except Exception:
            hijri_str = "—"
    else:
        hijri_str = "ثبّت hijri_converter"

    await event.respond(
        f"**التاريخ**\n\n"
        f"  ميلادي  :  `{mili}`\n"
        f"  هجري    :  `{hijri_str}`"
    )


# ── .يوم ─────────────────────────────────────────────────────────
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.يوم$"))
async def show_day(event):
    now = _now()
    day = DAYS_AR.get(now.strftime("%A"), now.strftime("%A"))
    await event.respond(f"اليوم هو: **{day}**")


# ── .منبه HH:MM ──────────────────────────────────────────────────
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.منبه (\d{1,2}):(\d{2})$"))
async def set_alarm(event):
    await event.delete()
    h = int(event.pattern_match.group(1))
    m = int(event.pattern_match.group(2))

    now    = _now()
    try:
        target = now.replace(hour=h, minute=m, second=0, microsecond=0)
    except ValueError:
        return await event.respond("وقت غير صحيح")

    if target <= now:
        target += timedelta(days=1)

    diff = (target - now).total_seconds()
    hrs  = int(diff // 3600)
    mins = int((diff % 3600) // 60)

    await event.respond(
        f"**تم ضبط المنبه**\n\n"
        f"  الوقت     :  `{h:02d}:{m:02d}`\n"
        f"  بعد       :  {hrs}س {mins}د"
    )

    await asyncio.sleep(diff)
    await client.send_message("me", f"**المنبه:** الساعة `{h:02d}:{m:02d}`")


# ── .عداد ثواني ──────────────────────────────────────────────────
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.عداد (\d+)$"))
async def countdown(event):
    secs = min(int(event.pattern_match.group(1)), 3600)
    msg  = await event.respond(f"**عداد:** `{secs}` ثانية")

    for remaining in range(secs - 1, -1, -1):
        await asyncio.sleep(1)
        if remaining % 10 == 0 or remaining <= 10:
            try:
                await msg.edit(f"**عداد:** `{remaining}` ثانية")
            except Exception:
                break

    try:
        await msg.edit("**انتهى العداد!**")
    except Exception:
        pass


# ── .مدة يوم/شهر/سنة ────────────────────────────────────────────
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.مدة (\d{1,2})/(\d{1,2})/(\d{4})$"))
async def time_since(event):
    d = int(event.pattern_match.group(1))
    m = int(event.pattern_match.group(2))
    y = int(event.pattern_match.group(3))

    try:
        now   = _now()
        past  = datetime(y, m, d)
        delta = now.replace(tzinfo=None) - past
        days  = delta.days
        years     = days // 365
        months_r  = (days % 365) // 30
        days_r    = (days % 365) % 30

        await event.respond(
            f"**المدة منذ** `{d}/{m}/{y}`\n\n"
            f"  `{years}` سنة  —  `{months_r}` شهر  —  `{days_r}` يوم\n"
            f"  إجمالي الأيام  :  `{days}`"
        )
    except ValueError:
        await event.respond("تاريخ غير صحيح — الصيغة: `.مدة يوم/شهر/سنة`")
