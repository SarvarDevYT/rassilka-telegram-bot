# Render.com ga bepul 24/7 o'rnatish qo'llanmasi

Ushbu qo'llanma yordamida botingizni [Render.com](https://render.com) bepul bulutli hostingiga 10–15 daqiqada yuklab, 24/7 ishlatishingiz mumkin.

---

## 1-qadam: Sessiya matnini olish (Noutbukda)
Render.com da server har qayta ishga tushganda fayllar o'chib ketmasligi uchun sessiyani matn (`SESSION_STRING`) ko'rinishida olishimiz kerak:

1. Terminalda buyruq bering:
   ```bash
   python login_helper.py
   ```
2. Telegramingizga kelgan kodni kiriting.
3. Ekranga `RENDER / KOYEB BEPUL HOSTINGLARI UCHUN SESSION_STRING:` sarlavhasi ostida uzun matn chiqadi. **Uni nusxalab (copy qilib) oling.**

---

## 2-qadam: Loyihani GitHub ga yuklash
1. [github.com](https://github.com) ga kiring va yangi repozitoriy oching (nomi: masalan `rassilka-bot`).
   * **Muhim:** Repozitoriyni **Private** (shaxsiy) qilib oching.
2. Noutbukingizdagi terminalda quyidagi buyruqlarni ketma-ket bajaring:
   ```bash
   git init
   git add .
   git commit -m "first commit"
   git branch -M main
   git remote add origin https://github.com/USERNAME/rassilka-bot.git
   git push -u origin main
   ```
*(Eslatma: `.env` va sessiya fayllari `.gitignore` ga qo'shilgan, shuning uchun parollaringiz GitHubga chiqib ketmaydi).*

---

## 3-qadam: Render.com da Web Service yaratish
1. [render.com](https://render.com) saytiga kiring va GitHub akkauntingiz orqali kiring.
2. **"New +"** tugmasini bosib, **"Web Service"** ni tanlang.
3. GitHubdagi `rassilka-bot` repozitoriyingizni tanlang (**Connect** bosing).
4. Sozlamalarni quyidagicha to'ldiring:
   - **Name:** `rassilka-telegram-bot`
   - **Region:** `Frankfurt (EU Central)`
   - **Branch:** `main`
   - **Runtime:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python bot_admin.py`
   - **Instance Type:** **Free** ($0/month)

---

## 4-qadam: Muhit o'zgaruvchilarini kiritish (Environment Variables)
O'sha sahifaning pastki qismidagi **"Environment Variables"** bo'limiga quyidagi kalitlarni qo'shing:

| Key | Value |
|---|---|
| `BOT_TOKEN` | BotFather bergan token |
| `API_ID` | `32576096` |
| `API_HASH` | `aafedd2ddb073e77cc3ee6cc3b9ba6ee` |
| `PHONE_NUMBER` | `+998906066616` |
| `ADMIN_ID` | `6626402818` |
| `SESSION_STRING` | 1-qadamda login_helper bergan uzun sessiya matni |
| `DELAY_MIN` | `15` |
| `DELAY_MAX` | `30` |

So'ngra **"Deploy Web Service"** tugmasini bosing!

---

## 5-qadam: Render 24/7 uxlab qolmasligi uchun (Doimiy uyg'oq tutish)
Render bepul xizmati agar 15 daqiqa ichida saytga murojaat bo'lmasa, serverni "uxlatib" qo'yadi. Buning oldini olish juda oson:

1. Render sizga bergan havolani oling (masalan: `https://rassilka-bot-xxxx.onrender.com`).
2. Bepul [cron-job.org](https://cron-job.org) yoki [uptimerobot.com](https://uptimerobot.com) saytiga kiring.
3. Yangi vazifa (monitor) qo'shib, havolangizni har **10 daqiqada** bir marta tekshiradigan (ping qiladigan) qilib qo'ying.
4. **Natija:** Server hech qachon uxlamaydi va botingiz butun oy davomida 24/7 uzluksiz ishlab turadi!
