import asyncio
import os
import sys
from pathlib import Path
import qrcode
from telethon import TelegramClient, errors
from telethon.sessions import StringSession
from config import API_HASH, API_ID, PHONE_NUMBER, SESSION_NAME, validate_config


async def login_via_qr(client: TelegramClient):
    """Telegram ilovasi orqali QR-kodni skaner qilib bir zumda kirish."""
    print("\n" + "=" * 60)
    print("  1-USUL: QR-KOD ORQALI BIR ZUMDA KIRISH (KOD KUTISH SHART EMAS!)")
    print("=" * 60)
    print("Telegram serveridan QR-kod yaratilmoqda...")

    qr_login = await client.qr_login()

    # QR rasmni loyiha papkasiga saqlash
    qr_img = qrcode.make(qr_login.url)
    qr_file_path = Path("qr_login.png").resolve()
    qr_img.save(qr_file_path)

    print("\n" + "-" * 60)
    print("  QADAMLAR:")
    print("  1. Telefoningizda Telegram ilovasini oching.")
    print("  2. Sozlamalar (Настройки) -> Qurilmalar (Устройства) bo'limiga kiring.")
    print("  3. 'Qurilmani ulash' (Подключить устройство) tugmasini bosing.")
    print(f"  4. Kamerani ushbu papkadagi '{qr_file_path.name}' rasmiga qarating!")
    print("-" * 60)

    # Terminalda ham ASCII QR-kodni ko'rsatish
    qr_terminal = qrcode.QRCode()
    qr_terminal.add_data(qr_login.url)
    try:
        qr_terminal.print_ascii(invert=True)
    except Exception:
        pass

    print(f"\n[!] Agar terminalda QR ko'rinmasa, mana bu rasmni ochib skaner qiling:")
    print(f"    👉 {qr_file_path}")
    print("\n⏳ Skaner qilishingiz kutilmoqda...")

    try:
        user = await qr_login.wait()
    except errors.SessionPasswordNeededError:
        print("\n🔐 Akkauntingizda 2-bosqichli parol (Two-Step Verification) bor.")
        pwd = input("Iltimos, Telegram parolingizni kiriting: ").strip()
        user = await client.sign_in(password=pwd)

    return user


async def login_via_code(client: TelegramClient):
    """Oddiy telefon raqam va kod orqali kirish."""
    print(f"\n[!] {PHONE_NUMBER} raqamiga kod so'rovi yuborilmoqda...")
    sent_code = await client.send_code_request(PHONE_NUMBER)
    print("\n✅ Kod Telegram ilovangizga yuborildi.")
    code = input("Telegramdan kelgan kodni kiriting: ").strip().replace(" ", "").replace("-", "")

    try:
        user = await client.sign_in(PHONE_NUMBER, code, phone_code_hash=sent_code.phone_code_hash)
    except errors.SessionPasswordNeededError:
        print("\n🔐 Akkauntingizda 2-bosqichli parol yoqilgan.")
        pwd = input("Iltimos, Telegram parolingizni kiriting: ").strip()
        user = await client.sign_in(password=pwd)

    return user


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

    print("\nKirish usulini tanlang:")
    print("1 - QR-kod orqali kirish (Tavsiya etiladi, hech qanday kod kutmaysiz! 🚀)")
    print("2 - Telefon raqamga SMS / Kod orqali kirish")
    choice = input("\nTanlovingiz (1 yoki 2, bo'sh qoldirilsa 1): ").strip()

    try:
        if choice == "2":
            user = await login_via_code(client)
        else:
            user = await login_via_qr(client)
    except Exception as e:
        print(f"\n[XATO] Kirishda xatolik yuz berdi: {e}")
        await client.disconnect()
        return

    me = await client.get_me()
    string_session_val = StringSession.save(client.session)

    # Rasm faylini tozalash
    try:
        Path("qr_login.png").unlink(missing_ok=True)
    except Exception:
        pass

    print("\n" + "=" * 60)
    print("  TABRIKLAYMIZ! AKKAUNT MUVAFFAQIYATLI ULINDI!")
    print("=" * 60)
    print(f" - Ism: {me.first_name}")
    print(f" - Username: @{me.username}" if me.username else " - Username: yo'q")
    print(f" - Telefon: +{me.phone}")
    print("\n[!] RENDER.COM DA 'SESSION_STRING' DEGAN JOYGA QUYIDAGI MATNNI QO'YASIZ:")
    print("-" * 60)
    print(string_session_val)
    print("-" * 60)
    print("=" * 60)

    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
