# ════════════════════════════════════════
#  Satoru — م15: النطق (TTS/STT)
# ════════════════════════════════════════
import os, asyncio, random
from satoru import client
from telethon import events

TEMP_DIR = "temp_audio"
os.makedirs(TEMP_DIR, exist_ok=True)


def _tmp(ext="mp3") -> str:
    return os.path.join(TEMP_DIR, f"satoru_{random.randint(10000, 99999)}.{ext}")


def _tts_sync(text: str, lang: str = "ar") -> str | None:
    """
    تحويل النص لصوت باستخدام gTTS
    إذا لم يكن مثبتاً، يحاول استخدام Google TTS مباشرة
    """
    fp = _tmp("mp3")
    text = text[:500]  # حد أقصى 500 حرف

    # المحاولة الأولى: gTTS
    try:
        from gtts import gTTS
        tts = gTTS(text=text, lang=lang, slow=False)
        tts.save(fp)
        if os.path.exists(fp) and os.path.getsize(fp) > 0:
            return fp
    except ImportError:
        pass
    except Exception:
        pass

    # المحاولة الثانية: edge-tts
    try:
        import subprocess, sys
        voice_map = {"ar": "ar-SA-ZariyahNeural", "en": "en-US-JennyNeural"}
        voice = voice_map.get(lang, "ar-SA-ZariyahNeural")
        result = subprocess.run(
            [sys.executable, "-m", "edge_tts", "--voice", voice, "--text", text, "--write-media", fp],
            capture_output=True, timeout=30
        )
        if result.returncode == 0 and os.path.exists(fp) and os.path.getsize(fp) > 0:
            return fp
    except Exception:
        pass

    # المحاولة الثالثة: Google Translate TTS
    try:
        import urllib.request, urllib.parse
        encoded = urllib.parse.quote(text[:200])
        url = (
            f"https://translate.google.com/translate_tts"
            f"?ie=UTF-8&tl={lang}&client=tw-ob&q={encoded}"
        )
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = resp.read()
            if len(data) > 1000:
                with open(fp, "wb") as f:
                    f.write(data)
                return fp
    except Exception:
        pass

    return None


# ── .انطق + نص (عربي) ────────────────────────────────────────────
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.انطق (.+)$"))
async def tts_arabic(event):
    await event.delete()
    text = event.pattern_match.group(1)
#    msg  = await event.respond("جاري التحويل للصوت...")

    fp = await asyncio.get_event_loop().run_in_executor(None, _tts_sync, text, "ar")

    if fp and os.path.exists(fp):
        try:
            await client.send_file(
                event.chat_id, fp,
                voice_note=True,
                caption=f"`{text[:80]}`"
            )
        finally:
            try: os.remove(fp)
            except Exception: pass
        await event.delete()
    else:
        await msg.edit(
            "فشل تحويل النص لصوت\n\n"
            "ثبّت المكتبات اللازمة:\n"
            "`.نصب gtts`"
        )


# ── .انطقen + نص (إنجليزي) ──────────────────────────────────────
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.انطقen (.+)$"))
async def tts_english(event):
    await event.delete()
    text = event.pattern_match.group(1)
    msg  = await event.respond("Converting to voice...")

    fp = await asyncio.get_event_loop().run_in_executor(None, _tts_sync, text, "en")

    if fp and os.path.exists(fp):
        try:
            await client.send_file(
                event.chat_id, fp,
                voice_note=True,
                caption=f"`{text[:80]}`"
            )
        finally:
            try: os.remove(fp)
            except Exception: pass
        await event.delete()
    else:
        await msg.edit("TTS failed — install: `.نصب gtts`")


# ── .وشيقول (بالرد على فويس) ─────────────────────────────────────
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.وشيقول$"))
async def stt(event):
    await event.delete()
    reply = await event.get_reply_message()
    if not reply or not reply.voice:
        return await event.respond("يجب الرد على رسالة صوتية (فويس)")

    msg = await event.respond("جاري التعرف على الصوت...")

    ogg_path = _tmp("ogg")
    wav_path = _tmp("wav")

    try:
        await reply.download_media(file=ogg_path)

        # تحويل OGG → WAV
        try:
            from pydub import AudioSegment
            sound = AudioSegment.from_ogg(ogg_path)
            sound.export(wav_path, format="wav")
        except ImportError:
            return await msg.edit("ثبّت pydub: `.نصب pydub`")

        # التعرف على الكلام
        try:
            import speech_recognition as sr
            r_obj = sr.Recognizer()
            with sr.AudioFile(wav_path) as src:
                audio = r_obj.record(src)
            text = r_obj.recognize_google(audio, language="ar-SA")
            await msg.edit(f"**يقول:**\n{text}")
        except ImportError:
            await msg.edit("ثبّت SpeechRecognition: `.نصب SpeechRecognition`")
        except Exception as e:
            await msg.edit(f"لم يتم التعرف على الكلام: {e}")

    except Exception as e:
        await msg.edit(f"خطأ: {e}")
    finally:
        for p in [ogg_path, wav_path]:
            try: os.remove(p)
            except Exception: pass
