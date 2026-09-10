import asyncio
import logging
import os
import random
import sys
from datetime import datetime
from pathlib import Path

from aiogram import Bot, Dispatcher, F, types
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    CallbackQuery,
    FSInputFile,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from config import (
    ADMIN_IDS,
    BOT_TOKEN,
    DELAY_MAX,
    DELAY_MIN,
    REPORTS_DIR,
    UPLOADS_DIR,
    validate_config,
)
from excel_parser import parse_excel_file
from report_generator import generate_excel_report
from telegram_client import check_and_send_message, ensure_connected

# Log sozlamalari
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Holatlar (FSM)
class BroadcastState(StatesGroup):
    waiting_for_excel = State()
    waiting_for_message = State()
    confirm_broadcast = State()
    is_broadcasting = State()


# Tugmalar
def get_main_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="📤 Yangi rassilka boshlash", callback_data="start_broadcast")],
        [InlineKeyboardButton(text="⚙️ Akkaunt holatini tekshirish", callback_data="check_account")],
        [InlineKeyboardButton(text="📊 Oxirgi hisobotni yuklab olish", callback_data="last_report")],
        [InlineKeyboardButton(text="ℹ️ Foydalanish yo'riqnomasi", callback_data="help_info")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_confirm_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(text="🚀 Yuborishni boshlash", callback_data="confirm_send"),
            InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_broadcast"),
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# Bot va Dispatcher
dp = Dispatcher()


# Admin tekshiruvi filtri
def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


@dp.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        await message.reply("⛔ Kechirasiz, siz ushbu botning administratori emassiz.")
        return

    await state.clear()
    text = (
        f"👋 <b>Assalomu alaykum, {message.from_user.full_name}!</b>\n\n"
        f"Bu sizning shaxsiy Telegram akkauntingiz orqali Excel fayldagi mijozlarga "
        f"avtomatlashtirilgan xabar tarqatish (rassilka) boshqaruv panelingiz.\n\n"
        f"Quyidagi tugmalardan birini tanlang:"
    )
    await message.answer(text, reply_markup=get_main_keyboard(), parse_mode=ParseMode.HTML)


@dp.callback_query(F.data == "check_account")
async def cb_check_account(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Ruxsat yo'q", show_alert=True)
        return

    await callback.answer("Tekshirilmoqda...")
    is_ok, msg = await ensure_connected()
    if is_ok:
        text = f"✅ <b>Akkaunt holati a'lo:</b>\n{msg}"
    else:
        text = (
            f"❌ <b>Akkaunt ulanmagan:</b>\n{msg}\n\n"
            f"<i>Maslahat: Server yoki kompyuter konsolida <code>python login_helper.py</code> "
            f"skriptini ishga tushirib, bir marta akkauntga kiring.</i>"
        )
    await callback.message.edit_text(text, reply_markup=get_main_keyboard(), parse_mode=ParseMode.HTML)


@dp.callback_query(F.data == "help_info")
async def cb_help_info(callback: CallbackQuery):
    text = (
        "📖 <b>Rassilka tizimi bo'yicha qisqacha yo'riqnoma:</b>\n\n"
        "1. <b>Excel fayl tayyorlash:</b>\n"
        "   - Faylingizda kamida bitta <code>Telefon</code> ustuni bo'lishi kerak.\n"
        "   - Agar <code>Ism</code> ustuni bo'lsa, xabarga <code>{ism}</code> deb qo'shib yuborsangiz, har bir mijozga o'z ismi bilan boradi.\n\n"
        "2. <b>Xavfsizlik qoidalari (Anti-ban):</b>\n"
        f"   - Har bir xabar orasida {DELAY_MIN} dan {DELAY_MAX} sekundgacha tasodifiy tanaffus qilinadi.\n"
        "   - Telegram akkaunt bloklanmasligi uchun bir kunda 30–50 tadan ortiq begona raqamlarga birdaniga yozmaslik tavsiya etiladi.\n\n"
        "3. <b>Raqamlarni tekshirish:</b>\n"
        "   - Tizim avval raqamda Telegram akkaunt bormi-yo'qligini tekshiradi.\n"
        "   - Agar bo'lmasa, xabar yuborilmaydi va hisobotga kiritiladi."
    )
    await callback.message.edit_text(text, reply_markup=get_main_keyboard(), parse_mode=ParseMode.HTML)


@dp.callback_query(F.data == "last_report")
async def cb_last_report(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return

    reports = sorted(REPORTS_DIR.glob("report_*.xlsx"), key=os.path.getmtime, reverse=True)
    if not reports:
        await callback.answer("Hozircha hech qanday hisobot mavjud emas.", show_alert=True)
        return

    last_file = reports[0]
    await callback.answer("Hisobot yuborilmoqda...")
    doc = FSInputFile(str(last_file))
    await callback.message.answer_document(doc, caption=f"📊 Oxirgi hisobot fayli:\n<code>{last_file.name}</code>", parse_mode=ParseMode.HTML)


@dp.callback_query(F.data == "start_broadcast")
async def cb_start_broadcast(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return

    # Avval akkaunt ulanganligini tekshiramiz
    is_ok, msg = await ensure_connected()
    if not is_ok:
        await callback.answer("Akkaunt ulanmagan!", show_alert=True)
        await callback.message.answer(
            f"⚠️ <b>Xabar yuboruvchi akkaunt hali ulanmagan!</b>\n\n{msg}\n\n"
            f"Iltimos, avval konsolda <code>python login_helper.py</code> orqali akkauntingizni ulang.",
            parse_mode=ParseMode.HTML,
        )
        return

    await state.set_state(BroadcastState.waiting_for_excel)
    await callback.message.answer(
        "📁 <b>Excel faylni (.xlsx, .xls yoki .csv) ushbu botga hujjat (document) sifatida yuboring:</b>\n\n"
        "<i>Eslatma: Faylda telefon raqamlari ustuni bo'lishi shart.</i>",
        parse_mode=ParseMode.HTML,
    )
    await callback.answer()


@dp.message(BroadcastState.waiting_for_excel, F.document)
async def handle_excel_upload(message: Message, state: FSMContext, bot: Bot):
    if not is_admin(message.from_user.id):
        return

    doc = message.document
    filename = doc.file_name or "data.xlsx"
    ext = Path(filename).suffix.lower()

    if ext not in [".xlsx", ".xls", ".csv"]:
        await message.reply("❌ Faqat <b>.xlsx</b>, <b>.xls</b> yoki <b>.csv</b> formatdagi fayllarni yuboring!", parse_mode=ParseMode.HTML)
        return

    processing_msg = await message.reply("⏳ Fayl yuklab olinmoqda va tahlil qilinmoqda...")
    saved_path = UPLOADS_DIR / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"

    try:
        await bot.download(doc, destination=saved_path)
        parsed = parse_excel_file(saved_path)

        valid_count = parsed["valid_count"]
        if valid_count == 0:
            await processing_msg.edit_text("❌ Faylda birorta ham yaroqli telefon raqam topilmadi!")
            return

        await state.update_data(
            excel_path=str(saved_path),
            records=parsed["records"],
            phone_col=parsed["phone_column"],
            name_col=parsed["name_column"],
        )

        name_info = f"Topilgan ism ustuni: <b>{parsed['name_column']}</b>" if parsed['name_column'] else "Ism ustuni topilmadi (ixtiyoriy)"
        await processing_msg.edit_text(
            f"✅ <b>Fayl muvaffaqiyatli tahlil qilindi!</b>\n\n"
            f"📊 Jami qatorlar: <b>{parsed['total_rows']}</b>\n"
            f"🎯 Toza raqamlar soni: <b>{valid_count}</b>\n"
            f"📞 Telefon ustuni: <b>{parsed['phone_column']}</b>\n"
            f"👤 {name_info}\n\n"
            f"✍️ <b>Endi mijozlarga yuboriladigan xabar matnini yozing:</b>\n"
            f"<i>(Agar ismni qo'shmoqchi bo'lsangiz, matn ichida <code>{{ism}}</code> deb yozing, masalan: 'Assalomu alaykum, {{ism}}!')</i>",
            parse_mode=ParseMode.HTML,
        )
        await state.set_state(BroadcastState.waiting_for_message)

    except Exception as e:
        logger.error(f"Fayl tahlilida xatolik: {e}")
        await processing_msg.edit_text(f"❌ Faylni o'qishda xatolik: {str(e)}")


@dp.message(BroadcastState.waiting_for_message, F.text)
async def handle_broadcast_text(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return

    broadcast_text = message.text.strip()
    data = await state.get_data()
    records = data.get("records", [])

    await state.update_data(message_text=broadcast_text)
    await state.set_state(BroadcastState.confirm_broadcast)

    sample_name = records[0].get("name") if records else "Mijoz"
    sample_preview = broadcast_text.replace("{ism}", sample_name or "Ali")

    await message.answer(
        f"📝 <b>Xabar matni qabul qilindi!</b>\n\n"
        f"<b>Namuna ko'rinishi (birinchi mijoz uchun):</b>\n"
        f"────────────────────\n"
        f"{sample_preview}\n"
        f"────────────────────\n\n"
        f"👥 Qabul qiluvchilar soni: <b>{len(records)} ta</b>\n"
        f"⏱ Har bir xabar oralig'i: <b>{DELAY_MIN}–{DELAY_MAX} sekund</b>\n\n"
        f"Rassilkani boshlaymizmi?",
        reply_markup=get_confirm_keyboard(),
        parse_mode=ParseMode.HTML,
    )


@dp.callback_query(F.data == "cancel_broadcast")
async def cb_cancel_broadcast(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❌ Rassilka bekor qilindi.", reply_markup=get_main_keyboard())
    await callback.answer()


@dp.callback_query(F.data == "confirm_send")
async def cb_confirm_send(callback: CallbackQuery, state: FSMContext, bot: Bot):
    if not is_admin(callback.from_user.id):
        return

    data = await state.get_data()
    records = data.get("records", [])
    message_text = data.get("message_text", "")

    if not records or not message_text:
        await callback.answer("Ma'lumotlar topilmadi, qaytadan boshlang.", show_alert=True)
        await state.clear()
        return

    await state.set_state(BroadcastState.is_broadcasting)
    await callback.answer("Rassilka boshlandi!")

    status_msg = await callback.message.edit_text(
        f"🚀 <b>Rassilka boshlandi!</b>\n\n"
        f"Jami: <b>{len(records)} ta</b>\n"
        f"Yuborildi: <b>0</b>\n"
        f"Telegram yo'q: <b>0</b>\n"
        f"Xatolar: <b>0</b>\n"
        f"Jarayon: <b>0%</b>",
        parse_mode=ParseMode.HTML,
    )

    results = []
    sent_count = 0
    no_tg_count = 0
    error_count = 0
    total = len(records)

    for i, item in enumerate(records, start=1):
        phone = item["phone"]
        name = item.get("name", "")

        res = await check_and_send_message(phone=phone, message_text=message_text, name=name)
        res["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        results.append(res)

        if res["status"] == "SENT":
            sent_count += 1
        elif res["status"] == "NO_TELEGRAM":
            no_tg_count += 1
        else:
            error_count += 1

        # Har 3-5 ta raqamda yoki oxirida progress xabarini yangilash
        if i % 3 == 0 or i == total:
            percent = int((i / total) * 100)
            try:
                await status_msg.edit_text(
                    f"⏳ <b>Rassilka davom etmoqda...</b>\n\n"
                    f"Jarayon: <b>{i} / {total} ({percent}%)</b>\n"
                    f"✅ Yuborildi: <b>{sent_count}</b>\n"
                    f"❌ Telegram yo'q: <b>{no_tg_count}</b>\n"
                    f"⚠️ Boshqa xatolar: <b>{error_count}</b>",
                    parse_mode=ParseMode.HTML,
                )
            except Exception:
                pass

        # Agar Telegram akkaunt spam-blok (PeerFlood) bersa, darhol to'xtatish!
        if res.get("status") == "FLOOD_BLOCKED":
            await bot.send_message(
                callback.from_user.id,
                "⛔ <b>DIQQAT! Telegram akkauntingizga spam cheklovi qo'yildi. Akkauntni asrash uchun rassilka zudlik bilan to'xtatildi!</b>",
                parse_mode=ParseMode.HTML,
            )
            break

        # Tanaffus (Anti-spam kechikish)
        if i < total:
            sleep_time = random.uniform(DELAY_MIN, DELAY_MAX)
            await asyncio.sleep(sleep_time)

    # Yakuniy hisobot yaratish
    report_file = generate_excel_report(results)

    await state.clear()

    final_text = (
        f"🎉 <b>Rassilka yakunlandi!</b>\n\n"
        f"📊 Jami tekshirildi: <b>{len(results)} ta</b>\n"
        f"✅ Muvaffaqiyatli yuborildi: <b>{sent_count} ta</b>\n"
        f"❌ Telegram yo'q: <b>{no_tg_count} ta</b>\n"
        f"⚠️ Yuborilmadi/xatolar: <b>{error_count} ta</b>\n\n"
        f"Batafsil natijalar quyidagi Excel faylda keltirilgan:"
    )
    await bot.send_message(callback.from_user.id, final_text, parse_mode=ParseMode.HTML)

    doc = FSInputFile(str(report_file))
    await bot.send_document(
        callback.from_user.id,
        doc,
        caption=f"📋 Rassilka hisoboti ({report_file.name})",
        reply_markup=get_main_keyboard(),
    )


from aiohttp import web
from config import PORT


async def start_web_server():
    """Render.com Web Service uchun health check web serveri"""
    app = web.Application()

    async def handle_health(request):
        return web.Response(text="OK: Telegram Rassilka Bot is Running!", status=200)

    app.router.add_get("/", handle_health)
    app.router.add_get("/health", handle_health)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    logger.info(f"Health-check web serveri {PORT}-portda ishga tushdi.")


async def main():
    errors = validate_config(require_bot=True, require_userbot=False)
    if errors:
        logger.error(f".env sozlamalarida xatolik: {errors}")
        print("XATOLIK: .env faylida kerakli parametrlar mavjud emas:")
        for e in errors:
            print(f" - {e}")
        return

    bot = Bot(token=BOT_TOKEN)
    logger.info("Admin bot ishga tushmoqda...")
    print("\n" + "=" * 50)
    print("  TELEGRAM RASSILKA ADMIN BOTI ISHGA TUSHDI!")
    print("=" * 50)
    print("Botga o'tib /start buyrug'ini bosing.\n")

    # Render.com kabi hostinglar uchun web serverni fonda yoqish
    try:
        await start_web_server()
    except Exception as e:
        logger.warning(f"Web serverni ishga tushirishda ogohlantirish: {e}")

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
