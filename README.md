# Telegram Rassilka Boti (Excel fayldan shaxsiy akkaunt orqali xabar tarqatish)

Ushbu dastur orqali siz Excel fayldagi telefon raqamlarni avtomatik tarzda Telegram bor-yo'qligini tekshirib, shaxsiy Telegram akkauntingiz nomidan foydalanuvchilarga xabarlarni xavfsiz va ketma-ket yuborishingiz mumkin.

---

## Asosiy imkoniyatlar:
- 📥 **Excel (.xlsx, .xls) va CSV yuklash**: Ustunlarni (Telefon, Ism) avtomatik aniqlaydi va raqamlarni tozalaydi.
- 🔍 **Telegram bor/yo'qligini tekshirish**: Agar raqamda Telegram bo'lmasa, xabar yuborilmaydi va vaqt tejaladi.
- 🛡️ **Spam-blokdan himoya (Anti-flood)**: Har bir xabar orasida 15–30 soniyalik tasodifiy tanaffus qilinadi. Telegram spam cheklovi sezilsa, akkauntni asrash uchun rassilka avtomatik to'xtatiladi.
- 👤 **Shaxsiylashtirilgan xabarlar**: Xabar matniga `{ism}` tegini qo'shsangiz, har bir mijozga o'z ismi bilan murojaat qilinadi (masalan: *Assalomu alaykum, Ali!*).
- 📊 **Batafsil Excel hisobot**: Tarqatish yakunida qaysi raqamga yetkazildi, qaysi birida Telegram yo'q yoki qanday xatolik bo'lgani haqida to'liq hisobot fayli taqdim etiladi.
- 🤖 **Qulay Admin Bot**: Barcha boshqaruv qulay Telegram bot orqali amalga oshiriladi.

---

## 1. O'rnatish va sozlash

### 1-qadam: Kutubxonalarni o'rnatish
```bash
pip install -r requirements.txt
```

### 2-qadam: .env faylini yaratish
Loyiha papkasida `.env` nomli fayl yarating va quyidagi ma'lumotlarni to'ldiring:

```env
# BotFather bergan bot tokeni
BOT_TOKEN=1234567890:AAHxxxxxxxxx

# my.telegram.org dan olingan ma'lumotlar
API_ID=12345678
API_HASH=abcdef0123456789abcdef0123456789

# Xabar yuboriladigan shaxsiy akkaunt telefon raqami
PHONE_NUMBER=+998901234567

# Sizning shaxsiy Telegram ID raqamingiz (@userinfobot dan bilib olish mumkin)
ADMIN_ID=987654321

# Xabarlar orasidagi kechikish (sekundlarda, tavsiya: 15-30)
DELAY_MIN=15
DELAY_MAX=30
```

---

## 2. Birinchi marta shaxsiy akkauntga kirish

Shaxsiy akkaunt sessiyasini bir marta yaratib olish uchun konsolda quyidagi buyruqni bering:
```bash
python login_helper.py
```
- Akkaunt raqamingizga Telegramdan kelgan kodni kiriting.
- Agar 2-bosqichli parol (Two-Step Verification) bo'lsa, uni ham kiriting.
- Sessiya `sessions/user_session.session` fayliga saqlanadi. Endi qayta kod so'ramaydi.

---

## 3. Botni ishga tushirish

```bash
python bot_admin.py
```

Endi Telegramda o'z botingizga kiring va `/start` tugmasini bosing:
1. **"Yangi rassilka boshlash"** tugmasini bosing.
2. Excel faylni hujjat ko'rinishida yuboring.
3. Xabar matnini kiriting.
4. **"Yuborishni boshlash"** tugmasini bosing.
5. Rassilka tugagach, bot sizga tayyor `report_...xlsx` hisobotini jo'natadi!
