import asyncio
import os
import sys
from telethon import TelegramClient
from config import API_HASH, API_ID, PHONE_NUMBER, SESSION_NAME, validate_config


async def main():
    print("=" * 60)
    print("      TELEGRAM AKKAUNTGA KIRISH VA SESSIYA YARATISH")
    print("=" * 60)

    errors = validate_config(require_bot=False, require_userbot=True)
    if errors:
        print("\nXATOLIK: .env faylida ma'lumotlar to'liq emas:")
        for err in errors:
            print(f" - {err}")
        print("\nIltimos, avval .env faylini to'ldiring!")
        sys.exit(1)

    print(f"\nUlanish parametrlari:")
    print(f" - API_ID: {API_ID}")
    print(f" - Telefon raqam: {PHONE_NUMBER}")
    print(f" - Sessiya fayli: {SESSION_NAME}.session")
    print("-" * 60)

    client = TelegramClient(SESSION_NAME, int(API_ID), API_HASH)
    await client.connect()

    if await client.is_user_authorized():
        me = await client.get_me()
        print(f"\n[OK] Akkaunt allaqachon ulangan!")
        print(f" - Ism: {me.first_name}")
        print(f" - Username: @{me.username}" if me.username else " - Username: yo'q")
        print(f" - Telefon: +{me.phone}")
        print("\nSessiya tayyor. Endi botni ishga tushirishingiz mumkin: python bot_admin.py")
        await client.disconnect()
        return

    print("\n[!] Telegram akkauntingizga bir martalik kirish kodi yuboriladi...")
    try:
        await client.start(phone=PHONE_NUMBER)
        me = await client.get_me()
        
        # Hostinglar (Render / Koyeb) uchun StringSession olish
        from telethon.sessions import StringSession
        string_session_val = StringSession.save(client.session)

        print("\n" + "=" * 60)
        print("  TABRIKLAYMIZ! AKKAUNT MUVAFFAQIYATLI ULINDI!")
        print("=" * 60)
        print(f" - Ism: {me.first_name}")
        print(f" - Username: @{me.username}" if me.username else " - Username: yo'q")
        print(f" - Telefon: +{me.phone}")
        print(f"\n[1] Mahalliy sessiya saqlandi: {SESSION_NAME}.session")
        print("\n[2] RENDER / KOYEB BEPUL HOSTINGLARI UCHUN SESSION_STRING:")
        print("-" * 60)
        print(string_session_val)
        print("-" * 60)
        print("Ushbu matnni Render.com dagi 'SESSION_STRING' muhit o'zgaruvchisiga qo'yasiz.")
        print("\nEndi botni to'liq ishga tushirishingiz mumkin: python bot_admin.py")
    except Exception as e:
        print(f"\n[XATO] Kirishda xatolik yuz berdi: {e}")
    finally:
        await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
