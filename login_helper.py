import asyncio
import os
import sys
from telethon import TelegramClient, errors, types
from telethon.sessions import StringSession
from config import API_HASH, API_ID, PHONE_NUMBER, SESSION_NAME, validate_config


async def main():
    print("=" * 60)
    print("      TELEGRAM AKKAUNTGA KIRISH VA SESSIYA YARATISH")
    print("=" * 60)

    errors_list = validate_config(require_bot=False, require_userbot=True)
    if errors_list:
        print("\nXATOLIK: .env faylida ma'lumotlar to'liq emas:")
        for err in errors_list:
            print(f" - {err}")
        sys.exit(1)

    client = TelegramClient(SESSION_NAME, int(API_ID), API_HASH)
    await client.connect()

    if await client.is_user_authorized():
        me = await client.get_me()
        string_session_val = StringSession.save(client.session)
        print(f"\n[OK] Akkaunt allaqachon ulangan: {me.first_name} (+{me.phone})")
        print("\n" + "=" * 60)
        print("  RENDER UCHUN SESSION_STRING:")
        print("=" * 60)
        print(string_session_val)
        print("=" * 60)
        await client.disconnect()
        return

    print(f"\n[!] {PHONE_NUMBER} raqamingizga kod so'rovi yuborilmoqda...")
    try:
        sent_code = await client.send_code_request(PHONE_NUMBER)
    except errors.FloodWaitError as e:
        print(f"\n[XATO] Telegram vaqtinchalik limit qo'ydi: {e.seconds} sekund kuting.")
        await client.disconnect()
        return
    except Exception as e:
        print(f"\n[XATO] Kod so'rashda xatolik: {e}")
        await client.disconnect()
        return

    print("\n" + "=" * 60)
    print("  ✅ KOD TELEGRAM DASTURINGIZGA YUBORILDI!")
    print("=" * 60)
    print("👉 Kompyuteringizdagi Telegram (Unigram) dasturini oching:")
    print("   Chap tomondagi chatlar ro'yxatida ko'k ikonkali:")
    print("   'Коды подтверждения' (Verification Codes) degan chat bor.")
    print("   Aynan shu chatga hozir yangi 5 xonali kod keldi!")
    print("=" * 60)

    code = input("\nO'sha 5 xonali kodni bu yerga kiriting va Enter bosing: ").strip()
    code = code.replace(" ", "").replace("-", "")

    try:
        await client.sign_in(PHONE_NUMBER, code, phone_code_hash=sent_code.phone_code_hash)
    except errors.SessionPasswordNeededError:
        print("\n🔐 Akkauntingizda 2-bosqichli parol (Two-Step Verification) bor.")
        pwd = input("Iltimos, Telegram parolingizni kiriting va Enter bosing: ").strip()
        try:
            await client.sign_in(password=pwd)
        except Exception as e:
            print(f"\n[XATO] Parol noto'g'ri: {e}")
            await client.disconnect()
            return
    except Exception as e:
        print(f"\n[XATO] Kodni tasdiqlashda xatolik: {e}")
        await client.disconnect()
        return

    me = await client.get_me()
    string_session_val = StringSession.save(client.session)

    print("\n" + "=" * 60)
    print("  TABRIKLAYMIZ! AKKAUNT MUVAFFAQIYATLI ULINDI!")
    print("=" * 60)
    print(f" - Ism: {me.first_name}")
    print(f" - Username: @{me.username}" if me.username else " - Username: yo'q")
    print(f" - Telefon: +{me.phone}")
    print(f"\n[OK] Sessiya saqlandi: {SESSION_NAME}.session")
    print("\n[!] RENDER.COM UCHUN 'SESSION_STRING' MATNI:")
    print("-" * 60)
    print(string_session_val)
    print("-" * 60)
    print("Ushbu matnni Render.com dagi 'Environment' bo'limiga qo'yasiz.")
    print("=" * 60)

    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
