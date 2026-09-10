import asyncio
import logging
import random
from typing import Any, Optional
from telethon import TelegramClient, errors, functions, types
from telethon.sessions import StringSession
from config import API_HASH, API_ID, PHONE_NUMBER, SESSION_NAME, SESSION_STRING

logger = logging.getLogger(__name__)

# Global client obyekti
_client: Optional[TelegramClient] = None


def get_telegram_client() -> TelegramClient:
    """Telethon mijozini qaytaradi yoki yaratadi."""
    global _client
    if _client is None:
        if not API_ID or not API_HASH:
            raise ValueError("API_ID yoki API_HASH .env faylida ko'rsatilmagan!")
        session = StringSession(SESSION_STRING) if SESSION_STRING else SESSION_NAME
        _client = TelegramClient(session, int(API_ID), API_HASH)
    return _client


async def ensure_connected() -> tuple[bool, str]:
    """
    Telegram shaxsiy akkauntiga ulanish va avtorizatsiyani tekshiradi.
    Qaytaradi: (muvaffaqiyatlimi, xabar)
    """
    try:
        client = get_telegram_client()
        if not client.is_connected():
            await client.connect()

        if not await client.is_user_authorized():
            return False, "Akkaunt hali tizimga kirmagan. Iltimos, avval login_helper.py orqali kiring."

        me = await client.get_me()
        user_name = me.first_name or "Foydalanuvchi"
        username_str = f" (@{me.username})" if me.username else ""
        return True, f"Ulandi: {user_name}{username_str} (+{me.phone})"
    except Exception as e:
        logger.error(f"Ulanishda xatolik: {e}")
        return False, f"Ulanishda xato: {str(e)}"


async def check_and_send_message(
    phone: str,
    message_text: str,
    name: str = "",
) -> dict[str, Any]:
    """
    Raqamda Telegram bor-yo'qligini tekshiradi va mavjud bo'lsa xabar yuboradi.
    Natija lug'atini qaytaradi: status, details, user_id va h.k.
    """
    client = get_telegram_client()
    if not client.is_connected():
        await client.connect()

    # Ism bo'lsa matndagi {ism} yoki {name} tegini almashtirish
    personal_text = message_text
    if "{ism}" in personal_text:
        personal_text = personal_text.replace("{ism}", name if name else "hurmatli mijoz")
    if "{name}" in personal_text:
        personal_text = personal_text.replace("{name}", name if name else "hurmatli mijoz")

    # 1. Kontakt sifatida tekshirish
    contact_id = random.randint(100000, 999999)
    input_contact = types.InputPhoneContact(
        client_id=contact_id,
        phone=phone,
        first_name=name if name else "Mijoz",
        last_name="",
    )

    imported_user = None
    try:
        import_result = await client(functions.contacts.ImportContactsRequest([input_contact]))
        if import_result.users:
            imported_user = import_result.users[0]
        else:
            return {
                "status": "NO_TELEGRAM",
                "phone": phone,
                "name": name,
                "details": "Telegram akkaunt topilmadi",
            }
    except errors.FloodWaitError as e:
        logger.warning(f"FloodWait: {e.seconds} sekund kutish kerak")
        return {
            "status": "FLOOD_WAIT",
            "phone": phone,
            "name": name,
            "details": f"Telegram limit berdi ({e.seconds} sek kutish kerak)",
            "wait_seconds": e.seconds,
        }
    except Exception as e:
        logger.error(f"Kontakt import qilishda xatolik ({phone}): {e}")
        return {
            "status": "IMPORT_ERROR",
            "phone": phone,
            "name": name,
            "details": f"Tekshirishda xato: {str(e)}",
        }

    # 2. Xabar yuborish
    try:
        await client.send_message(imported_user, personal_text)
        send_status = "SENT"
        details = "Muvaffaqiyatli yetkazildi"
    except errors.UserPrivacyRestrictedError:
        send_status = "PRIVACY_RESTRICTED"
        details = "Foydalanuvchi begonalardan xabar olishni cheklagan (Maxfiylik)"
    except errors.PeerFloodError:
        send_status = "FLOOD_BLOCKED"
        details = "DIQQAT: Telegram akkauntingizga spam-cheklov (PeerFlood) qo'ydi! Tarqatish to'xtatildi."
    except errors.FloodWaitError as e:
        send_status = "FLOOD_WAIT"
        details = f"Telegram limit berdi ({e.seconds} sek kutish kerak)"
    except Exception as e:
        send_status = "SEND_ERROR"
        details = f"Xabar yuborishda xato: {str(e)}"

    # 3. Akkaunt kontaktlar ro'yxatini tozalash (ro'yxat to'lib ketmasligi uchun)
    try:
        if imported_user:
            await client(functions.contacts.DeleteContactsRequest(id=[imported_user]))
    except Exception as e:
        logger.debug(f"Kontaktni o'chirishda xatolik: {e}")

    return {
        "status": send_status,
        "phone": phone,
        "name": name,
        "details": details,
        "user_id": getattr(imported_user, "id", None),
    }
