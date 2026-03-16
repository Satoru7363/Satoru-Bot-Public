# ════════════════════════════════════════
#  Satoru — م1: التحميل والترفيه (النسخة المتوافقة مع أندرويد - إصدار MP3)
# ════════════════════════════════════════
import os, asyncio, random, re
import requests
from satoru import client
from telethon import events, types

TEMP_DIR = "./temp_dl"
os.makedirs(TEMP_DIR, exist_ok=True)

def _clean_filename(title):
    """تنظيف اسم الملف ليكون مقبولاً في نظام التشغيل"""
    if not title: 
        return f"track_{random.randint(1000, 9999)}"
    clean = re.sub(r'[\\/*?:"<>|]', "", title)
    return clean.strip()[:80]

async def _dl(url, audio_only=False):
    """التحميل المباشر المتوافق مع Pydroid 3"""
    try:
        import yt_dlp
    except ImportError:
        return None, None, None, None

    random_id = random.randint(10000, 99999)
    out_template = os.path.join(TEMP_DIR, f"satoru_{random_id}.%(ext)s")

    opts = {
        "outtmpl": out_template,
        "quiet": True,
"concurrent_fragment_downloads": 10,
        "no_warnings": True,
        "noplaylist": True,
        "http_headers": {
"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
"Accept-Language": "en-US,en;q=0.9"
},
        "writethumbnail": True, # تحميل الصورة المصغرة
    }

    if audio_only:
        # اختيار أفضل جودة صوت متوفرة مباشرة
        opts["format"] = "bestaudio[ext=m4a]/bestaudio/best"
    else:
        opts["format"] = "best[ext=mp4]/best"

    def run():
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            data = info['entries'][0] if 'entries' in info else info
            
            title = data.get("title") or "Unknown"
            artist = data.get("artist") or data.get("creator") or data.get("uploader") or data.get("channel") or data.get("uploader_id") or "Unknown"
            actual_file = ydl.prepare_filename(data)
            
            
            # التأكد من وجود الملف وتحديد مساره الحقيقي
            if not os.path.exists(actual_file):
                base = os.path.splitext(actual_file)[0]
                for ex in ["m4a", "mp3", "webm", "mp4", "mkv", "ogg", "opus"]:
                    if os.path.exists(f"{base}.{ex}"):
                        actual_file = f"{base}.{ex}"
                        break

            # البحث عن الصورة المصغرة المحملة
            thumbnail_file = None
            base_path = os.path.splitext(actual_file)[0]
            for ext in ["webp", "jpg", "jpeg", "png"]:
                thumb_path = f"{base_path}.{ext}"
                if os.path.exists(thumb_path):
                    thumbnail_file = thumb_path
                    break
            
            return actual_file, title, artist, thumbnail_file

    try:
        return await asyncio.get_event_loop().run_in_executor(None, run)
    except Exception as e:
        print(f"تحذير في التحميل: {e}")
        return None, None, None, None

async def _send_audio_logic(event, msg, fp, title, artist, thumbnail_file):
    """إرسال الملف كصوت مع إجبار امتداد .mp3 لضمان التشغيل"""
    if not fp or not os.path.exists(fp):
        return await msg.edit("❌ فشل تحميل الملف، تأكد من الرابط.")
    
    # إجبار الامتداد ليكون .mp3 ليتعرف عليه تليجرام كمشغل موسيقى
    safe_title = _clean_filename(title)
    new_name = os.path.join(TEMP_DIR, f"{safe_title}.mp3")
    
    try:
        # حتى لو كان الملف m4a أو opus، سنقوم بتغيير اسمه لـ mp3 
        # تليجرام ذكي كفاية لتشغيل الملف بناءً على محتواه بمجرد رؤية الامتداد mp3
        os.rename(fp, new_name)
    except:
        new_name = fp

    await msg.edit("يتم الارسال...")
    try:
        await client.send_file(
            event.chat_id, 
            new_name,
            thumb=thumbnail_file, # إرفاق الصورة كغلاف
            caption=f"**{title}**",
            # سمات الملف الصوتي لضمان ظهوره في مشغل الموسيقى (مهم جداً للتشغيل)
            attributes=[types.DocumentAttributeAudio(
                duration=180, 
                title=title, 
                performer=artist,
                voice=False # التأكد أنه ملف موسيقى وليس بصمة صوتية
            )]
        )
        await msg.delete()
    except Exception as e:
        await msg.edit(f"❌ خطأ أثناء الرفع: {e}")
    finally:
        # تنظيف الملفات
        if os.path.exists(new_name): os.remove(new_name)
        if fp != new_name and os.path.exists(fp): os.remove(fp)
        if thumbnail_file and os.path.exists(thumbnail_file): os.remove(thumbnail_file)

async def _send_video_logic(event, msg, fp, title):
    """إرسال الملف كفيديو"""
    if not fp or not os.path.exists(fp):
        return await msg.edit("❌ فشل تحميل الفيديو.")
    
    ext = os.path.splitext(fp)[1]
    safe_title = _clean_filename(title)
    new_name = os.path.join(TEMP_DIR, f"{safe_title}{ext}")
    
    try:
        os.rename(fp, new_name)
    except:
        new_name = fp

    await msg.edit(" جاري إرسال الفيديو...")
    try:
        await client.send_file(event.chat_id, new_name, caption=f"**{title}**")
        await msg.delete()
    except Exception as e:
        await msg.edit(f"❌ خطأ أثناء الرفع: {e}")
    finally:
        if os.path.exists(new_name): os.remove(new_name)
        if fp != new_name and os.path.exists(fp): os.remove(fp)

# ── الأوامر التشغيلية ──────────────────────────────────────────




# ── Spotify Fast Command ─────────────────────────

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.سبوتي (.+)$"))
async def spotify_audio(event):
    query = event.pattern_match.group(1)
    msg = await event.edit(f"🎧 Spotify: **{query}**")

    try:
        import yt_dlp

        def search_and_download():
            opts = {
                "format": "bestaudio/best",
                "quiet": True,
                "noplaylist": True,
                "outtmpl": os.path.join(TEMP_DIR, f"spotify_%(id)s.%(ext)s"),
                "writethumbnail": True,
                "http_headers": {
                    "User-Agent": "Mozilla/5.0"
                }
            }

            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(f"ytsearch1:{query}", download=True)
                data = info["entries"][0]

                title = data.get("title", "Unknown")
                artist = data.get("artist") or data.get("creator") or data.get("uploader") or data.get("channel") or data.get("uploader_id") or "Unknown"

                file_path = ydl.prepare_filename(data)

                if not os.path.exists(file_path):
                    base = os.path.splitext(file_path)[0]
                    for ext in ["m4a","mp3","webm","opus","ogg"]:
                        if os.path.exists(f"{base}.{ext}"):
                            file_path = f"{base}.{ext}"
                            break

                thumb = None
                base = os.path.splitext(file_path)[0]
                for ext in ["webp","jpg","jpeg","png"]:
                    p = f"{base}.{ext}"
                    if os.path.exists(p):
                        thumb = p
                        break

                return file_path, title, artist, thumb

        fp, title, artist, thumb = await asyncio.get_event_loop().run_in_executor(None, search_and_download)

        await _send_audio_logic(event, msg, fp, title, artist, thumb)

    except Exception as e:
        await msg.edit(f"❌ Spotify Error\n`{e}`")







@client.on(events.NewMessage(outgoing=True, pattern=r"^\.يوت (.+)$"))
async def yt_audio(event):
    query = event.pattern_match.group(1)
    msg = await event.edit(f" يوتيوب: **{query}**")
    fp, title, artist, thumb = await _dl(f"ytsearch1:{query}", audio_only=True)
    await _send_audio_logic(event, msg, fp, title, artist, thumb)

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.ساوند (.+)$"))
async def sc_audio(event):
    query = event.pattern_match.group(1)
    msg = await event.edit(f" ساوند كلاود: **{query}**")
    fp, title, artist, thumb = await _dl(f"scsearch1:{query}", audio_only=True)
    await _send_audio_logic(event, msg, fp, title, artist, thumb)

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.mp3 (.+)$"))
async def dl_mp3(event):
    url = event.pattern_match.group(1)
    msg = await event.edit(" جاري تحميل المقطع الصوتي...")
    fp, title, artist, thumb = await _dl(url, audio_only=True)
    await _send_audio_logic(event, msg, fp, title, artist, thumb)

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.mp4 (.+)$"))
async def dl_mp4(event):
    url = event.pattern_match.group(1)
    msg = await event.edit(" جاري تحميل مقطع الفيديو...")
    fp, title, _, _ = await _dl(url, audio_only=False)
    await _send_video_logic(event, msg, fp, title)

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.تيك (.+)$"))
async def dl_tiktok(event):
    url = event.pattern_match.group(1)
    msg = await event.edit(" جاري تحميل من TikTok...")
    fp, title, _, _ = await _dl(url, audio_only=False)
    await _send_video_logic(event, msg, fp, title)

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.انستا (.+)$"))
async def dl_insta(event):
    url = event.pattern_match.group(1)
    msg = await event.edit(" جاري تحميل من Instagram...")
    fp, title, _, _ = await _dl(url, audio_only=False)
    await _send_video_logic(event, msg, fp, title)

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.شازام$"))
async def shazam_song(event):
    reply = await event.get_reply_message()
    if not reply or not reply.media:
        return await event.edit("⚠️ يجب الرد على رسالة صوتية أو فيديو.")
    
    msg = await event.edit(" جاري التعرف على الموسيقى...")
    dl_path = await reply.download_media(file=TEMP_DIR)
    
    try:
        from shazamio import Shazam
        shazam = Shazam()
        out = await shazam.recognize_song(dl_path)
        track = out.get("track", {})
        if track:
            t = track.get("title"); a = track.get("subtitle")
            await msg.edit(f" **العنوان:** {t}\n👤 **الفنان:** {a}")
        else:
            await msg.edit("❌ لم يتم التعرف على الأغنية.")
    except Exception as e:
        await msg.edit(f"❌ خطأ: {e}")
    finally:
        if os.path.exists(dl_path): os.remove(dl_path)

# وظيفة تنظيف تلقائي للملفات المؤقتة كل ساعة
async def _cleanup_worker():
    while True:
        await asyncio.sleep(3600)
        for f in os.listdir(TEMP_DIR):
            try:
                os.remove(os.path.join(TEMP_DIR, f))
            except:
                pass

# تشغيل عامل التنظيف في الخلفية
loop = asyncio.get_event_loop()
if loop.is_running():
    loop.create_task(_cleanup_worker())

