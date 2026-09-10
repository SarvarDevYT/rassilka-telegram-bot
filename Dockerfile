FROM python:3.13-slim

WORKDIR /app

# Muhim tizim kutubxonalari
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Talablarni o'rnatish
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Loyiha kodlarini ko'chirish
COPY . .

# Papkalarni yaratish
RUN mkdir -p uploads reports sessions

# Ishga tushirish
CMD ["python", "bot_admin.py"]
