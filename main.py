#!/usr/bin/env python3
# ════════════════════════════════════════
#
#       S A T O R U   U S E R B O T
#       © Satoru — All Rights Reserved
#       v2.0
#
# ════════════════════════════════════════
import sys
import asyncio
from satoru import client
from database import db
import config

BANNER = """
╔══════════════════════════════════════╗
║                                      ║
║      S A T O R U  U S E R B O T     ║
║           © Satoru  v2.0             ║
║                                      ║
╚══════════════════════════════════════╝
"""


async def _startup():
    """يُشغَّل مرة واحدة عند الإقلاع"""
    me = await client.get_me()

    # احفظ owner_id تلقائياً إذا كانت أول مرة
    if not db.get("owner_id"):
        db.set("owner_id", me.id)

    # تحديث config.OWNER_ID في الذاكرة
    config.OWNER_ID = db.get("owner_id", me.id)

    print(BANNER)
    print(f"  مرحباً: {me.first_name} ({me.id})")
    print(f"  الـ Owner ID: {config.OWNER_ID}")

    # تحميل جميع البلجنز
    from plugins import load_all
    loaded = load_all()
    print(f"  البلجنز المحمّلة ({len(loaded)}): {', '.join(loaded)}")
    print("\n  ✅ Satoru يعمل! أرسل .الاوامر لعرض القوائم.\n")


async def main():
    await client.start()
    await _startup()
    await client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())
