# Python-ning eng yengil versiyasidan foydalanamiz
FROM python:3.11-slim

# Ishchi papkani belgilash
WORKDIR /app

# Muhit o'zgaruvchilari (Python xatolarini darrov ko'rsatishi uchun)
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Tizim paketlarini yangilash (Postgres va boshqalar uchun kerak bo'lishi mumkin)
RUN apt-get update && apt-get install -y gcc libpq-dev && apt-get clean

# Kutubxonalar ro'yxatini ko'chirish va o'rnatish
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Loyiha kodlarini to'liq ko'chirish
COPY . .

# Serverni ishga tushirish buyrug'i
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]