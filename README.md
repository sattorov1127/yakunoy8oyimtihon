🚀 Jobify - Next-Gen Job Matching & Recruitment API
Jobify — bu ish beruvchilar (HR) va nomzodlar o'rtasidagi aloqani ta'minlovchi, yuqori tezlikda ishlovchi asinxron backend platformasi. Loyiha FastAPI ning barcha zamonaviy imkoniyatlari, asinxron ORM va fondagi vazifalarni boshqarish tizimlari asosida qurilgan.

🛠 Texnologik Stek (Tech Stack)
Framework: FastAPI (Python 3.11+).

Database: PostgreSQL (Asinxron ulanish bilan).

ORM: SQLAlchemy (Asinxron rejimda).

Task Queue: Celery + Redis (Email xabarnomalar uchun).

Containerization: Docker & Docker Compose.

✨ Loyiha Imkoniyatlari (Features)
Xavfsiz Autentifikatsiya: JWT (JSON Web Tokens) asosidagi kirish tizimi.

Vakansiya Boshqaruvi: HRlar uchun vakansiya yaratish, tahrirlash va statusni boshqarish.

Resume Engine: Nomzodlar uchun PDF formatida rezyume yuklash va saqlash tizimi.

Apply Logic: Vakansiyalarga ariza topshirish va takroriy arizalarni tekshirish.

Real-time Notifications: Ariza holati o'zgarganda nomzodga bildirishnoma yuborish.

Favorite System: Ma'qul kelgan ishlarni saralanganlar ro'yxatiga qo'shish.

Background Tasks: Foydalanuvchi ro'yxatdan o'tganda avtomatik email xabarnomalarini yuborish.

📂 Loyiha Strukturasi (Project Structure)
Plaintext
app/
├── auth/          # Foydalanuvchi va token mantiqlari
├── vacancy/       # Ish e'lonlari bo'limi
├── apply/         # Ariza, Rezyume, Saralanganlar va Bildirishnomalar
├── core/          # Xavfsizlik, Celery vazifalari va sozlamalar
├── database.py    # Asinxron DB ulanishi (SQLAlchemy + asyncpg)
└── main.py        # Ilovaning kirish nuqtasi
docker-compose.yml # Infratuzilmani boshqarish
Dockerfile         # Python konteyner sozlamalari
⚙️ O'rnatish va Ishga Tushirish
1. Repozitoriyani klonlash
Bash
cd jobify
2. .env faylini sozlash
.env faylini yarating va quyidagi qiymatlarni kiriting:

Фрагмент кода
DATABASE_URL=postgresql+asyncpg://postgres:123@db:5432/jobify
SECRET_KEY=jobify-super-secret-key-2026
REDIS_URL=redis://redis:6379/0
3. Docker Compose orqali ishga tushirish
Bash
docker-compose up -d --build
Ushbu buyruq PostgreSQL, Redis, FastAPI va Celery Worker xizmatlarini avtomatik ko'taradi.

📡 API Endpoints (Asosiy nuqtalar)
🔑 Autentifikatsiya (Auth)
POST /auth/register - Yangi foydalanuvchi yaratish (HR yoki Nomzod).

POST /auth/login - JWT token olish.

💼 Vakansiyalar (Vacancy)
GET /vacancy/all - Barcha faol ish e'lonlari (Filtrlar bilan).

POST /vacancy/create - Yangi vakansiya (Faqat HR uchun).

📝 Arizalar va Rezyume (Apply & Resume)
POST /apply/resume/upload - Rezyume yuklash (PDF formatda).

POST /apply/vacancy - Vakansiyalarga ariza topshirish.

GET /apply/hr/list - HR uchun kelgan arizalar ro'yxati.

PATCH /apply/hr/status/{id} - Ariza holatini o'zgartirish.

⭐ Saralanganlar va Xabarlar (Favorites & Notifications)
POST /apply/favorite/{vac_id} - Saralanganlarga qo'shish.

GET /apply/notifications - Bildirishnomalarni ko'rish.

📄 API Documentatsiya
Server ishga tushgach, to'liq interaktiv dokumentatsiyani quyidagi manzillardan olishingiz mumkin:

Swagger UI: http://localhost:8000/docs

Redoc: http://localhost:8000/redoc

👨‍💻 Developer
Ism: Sattorov Ilhom

Role: Backend Developer (FastAPI Expert)

