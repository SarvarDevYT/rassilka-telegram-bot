import os
from pathlib import Path
from dotenv import load_dotenv

# .env faylini yuklash
BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"
load_dotenv(dotenv_path=ENV_PATH)

# Papkalarni yaratish
UPLOADS_DIR = BASE_DIR / "uploads"
REPORTS_DIR = BASE_DIR / "reports"
SESSIONS_DIR = BASE_DIR / "sessions"

UPLOADS_DIR.mkdir(exist_ok=True)
REPORTS_DIR.mkdir(exist_ok=True)
SESSIONS_DIR.mkdir(exist_ok=True)

# Konfiguratsiya o'zgaruvchilari
BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
API_ID = os.getenv("API_ID", "").strip()
API_HASH = os.getenv("API_HASH", "").strip()
PHONE_NUMBER = os.getenv("PHONE_NUMBER", "").strip()

# Admin ID larini ro'yxat ko'rinishida olish
admin_id_raw = os.getenv("ADMIN_ID", "").strip()
ADMIN_IDS = [int(i.strip()) for i in admin_id_raw.split(",") if i.strip().isdigit()]

# Xabarlar orasidagi kechikish (sekund)
DELAY_MIN = int(os.getenv("DELAY_MIN", "15"))
DELAY_MAX = int(os.getenv("DELAY_MAX", "30"))

# Telethon sessiya fayli yo'li yoki StringSession
SESSION_NAME = str(SESSIONS_DIR / "user_session")
SESSION_STRING = os.getenv("SESSION_STRING", "").strip()

# Hosting (Render) uchun web port
PORT = int(os.getenv("PORT", "8080"))


def validate_config(require_bot: bool = True, require_userbot: bool = True) -> list[str]:
    """Konfiguratsiya to'liqligini tekshirish"""
    errors = []
    if require_bot and not BOT_TOKEN:
        errors.append("BOT_TOKEN belgilanmagan (.env faylida)")
    if require_userbot:
        if not API_ID:
            errors.append("API_ID belgilanmagan (.env faylida)")
        if not API_HASH:
            errors.append("API_HASH belgilanmagan (.env faylida)")
        if not PHONE_NUMBER:
            errors.append("PHONE_NUMBER belgilanmagan (.env faylida)")
    if not ADMIN_IDS:
        errors.append("ADMIN_ID belgilanmagan (.env faylida)")
    return errors
