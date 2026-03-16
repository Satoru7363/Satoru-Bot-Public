# ⚡ Satoru Userbot — دليل التشغيل الكامل
> © Satoru — All Rights Reserved

---

## 📋 المتطلبات

| المطلوب | الإصدار الأدنى |
|--------|----------------|
| Python | 3.10+ |
| pip    | مُثبَّت مع Python |

---

## 🚀 خطوات التشغيل

### الخطوة 1 — احصل على API_ID و API_HASH

1. افتح المتصفح واذهب إلى: **https://my.telegram.org/apps**
2. سجّل الدخول برقم هاتفك
3. اضغط **"API development tools"**
4. انسخ قيمتَي `app_api_id` و `app_api_hash`

---

### الخطوة 2 — تعديل ملف config.py

افتح الملف `config.py` وأدخل القيم:

```python
API_ID   = 123456        # ضع رقمك هنا
API_HASH = "abcdef..."   # ضع الـ hash هنا
```

> **SESSION** يُتركَ فارغاً، سيُحفظ تلقائياً في ملف `satoru_session.session` عند أول تشغيل.

---

### الخطوة 3 — تثبيت المكتبات

افتح Terminal في مجلد البوت، ثم:

```bash
pip install -r requirements.txt
```

للميزات الإضافية (تحميل يوتيوب + TTS):

```bash
pip install yt-dlp SpeechRecognition pydub hijri-converter
```

---

### الخطوة 4 — تشغيل البوت

```bash
python main.py
```

في أول مرة سيطلب منك:
- **رقم هاتفك** (بالصيغة الدولية مثل +9665xxxxxxxx)
- **كود التحقق** الذي يصلك على Telegram
- **كلمة مرور التحقق بخطوتين** (إذا كانت مفعّلة)

بعد ذلك يُحفظ الـ session تلقائياً ولن يُطلب منك مجدداً.

---

### الخطوة 5 — اختبار التشغيل

أرسل هذه الرسالة من حسابك في أي محادثة:

```
.فحص
```

إذا ردّ البوت فهو يعمل ✅

---

## 📱 أوامر البدء السريع

| الأمر | الوظيفة |
|-------|---------|
| `.الاوامر` | عرض القائمة الرئيسية (م1-م27) |
| `.م1` | قائمة اليوتيوب والترفيه |
| `.م5` | قائمة الخاص والردود |
| `.م11` | قائمة النشر التلقائي |
| `.فحص` | التحقق من حالة البوت |
| `.ping` | قياس سرعة الاستجابة |
| `.معلوماتي` | معلومات حسابك |

---

## 📂 هيكل المجلد

```
Satoru/
├── main.py              ← نقطة الانطلاق
├── config.py            ← الإعدادات (API_ID, API_HASH)
├── satoru.py            ← نسخة العميل (Telethon)
├── database.py          ← قاعدة البيانات (SQLite)
├── utils.py             ← أدوات مساعدة (تحويل الخطوط...)
├── requirements.txt     ← المكتبات المطلوبة
├── satoru_data.db       ← قاعدة البيانات (تُنشأ تلقائياً)
├── satoru_session.session ← الجلسة (تُنشأ تلقائياً)
├── saved_media/         ← ملفات الاختصارات
├── temp_audio/          ← ملفات صوتية مؤقتة
├── temp_dl/             ← تحميلات مؤقتة
└── plugins/
    ├── __init__.py      ← محمّل البلجنز التلقائي
    ├── menu.py          ← القوائم (م1-م27)
    ├── broadcast.py     ← م11: النشر التلقائي
    ├── private_reply.py ← م5: الخاص والردود
    ├── group.py         ← م4+م20: المجموعة والحماية
    ├── delete_copy.py   ← م6: المسح والنسخ
    ├── shortcuts.py     ← م7: الاختصارات والميمز
    ├── fonts.py         ← م14: الخطوط والترجمة
    ├── fun.py           ← م9+م10: التسلية
    ├── time_cmds.py     ← م3: الوقت والتاريخ
    ├── media_tts.py     ← م15: النطق (TTS/STT)
    ├── downloader.py    ← م15: التحميل (YT/TikTok/...)
    ├── games.py         ← م25: الألعاب ووعد
    ├── system.py        ← م17: النظام والتطوير
    ├── impersonate.py   ← م8: الانتحال والإرسال
    └── archive.py       ← م24: الأرشيف والبلاغات
```

---

## 🔐 الأمان

- البوت **لا يستجيب** إلا لرسائلك أنت (outgoing=True)
- **لا يرد** على أي شخص آخر في الأوامر
- في م5 يمكنك تفعيل الرد التلقائي للرسائل الواردة فقط إذا أردت
- الـ session محفوظ محلياً ولا يُرسل لأي جهة

---

## 🔄 التشغيل التلقائي (اختياري)

### Linux — systemd

```bash
sudo nano /etc/systemd/system/satoru.service
```

```ini
[Unit]
Description=Satoru Userbot
After=network.target

[Service]
Type=simple
User=YOUR_USER
WorkingDirectory=/path/to/Satoru
ExecStart=/usr/bin/python3 /path/to/Satoru/main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable satoru
sudo systemctl start satoru
```

### Screen (أبسط)

```bash
screen -S satoru python main.py
# Ctrl+A ثم D للخروج دون إيقاف
```

---

## ⚠️ ملاحظات مهمة

1. **لا تشارك** ملف `satoru_session.session` أو `config.py` مع أي أحد
2. استخدم البوت **بمسؤولية** — الإساءة قد تؤدي لحظر حسابك
3. أوامر `.eval` و`.bash` للمطورين فقط — لا تشغّلها من رسائل الآخرين
4. لتحميل اليوتيوب يجب تثبيت `ffmpeg` على النظام:
   - Windows: من https://ffmpeg.org/download.html
   - Ubuntu: `sudo apt install ffmpeg`
   - macOS: `brew install ffmpeg`

---

## 💬 قائمة الأوامر السريعة

```
.الاوامر          ← القائمة الرئيسية
.م1 → .م27       ← كل قائمة فرعية

══ النشر التلقائي ══
.نشر 30 @group    ← نشر كل 30 ثانية
.نشر_كروبات 60   ← نشر في كل الجروبات
.ايقاف النشر      ← إيقاف كل نشر

══ الخاص ══
.تشغيل الرد       ← تشغيل رد تلقائي
.الرد جملة        ← رد مخصص (بالرد على الرسالة)
.كتم الخاص @user  ← كتم شخص في الخاص

══ المجموعة ══
.كتم @user        ← كتم شخص
.تثبيت           ← تثبيت رسالة
.منع كلمة         ← منع كلمة

══ الخطوط ══
.بولد نص          ← 𝗻𝗼𝗿𝗺𝗮𝗹
.إيطالي نص        ← 𝘪𝘵𝘢𝘭𝘪𝘤
.سكريبت نص        ← 𝓈𝒸𝓇𝒾𝓅𝓉

══ التحميل ══
.يوت اسم الاغنية  ← تحميل من يوتيوب
.تيك رابط         ← تحميل تيك توك
.mp3 رابط         ← تحميل صوت

══ النطق ══
.انطق مرحبا        ← تحويل النص لصوت
.وش_يقول          ← تحويل صوت لنص
```

---

*© Satoru Userbot v2.0 — All Rights Reserved*
