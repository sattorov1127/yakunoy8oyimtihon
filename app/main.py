import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqladmin import Admin

# Ma'lumotlar bazasi ulanishlari
from app.database import engine, Base

# Routerlarni import qilish
from app.auth.router import router as auth_router
from app.profile.router import router as profile_router
from app.vacancy.router import router as vacancy_router
from app.apply.router import router as apply_router

# Modellarni import qilish (Jadvallar yaratilishi uchun shart!)
from app.auth.models import User
from app.profile.models import CandidateProfile, CompanyProfile
from app.vacancy.models import Vacancy
from app.apply.models import Resume, Apply, Notification

# Admin ko'rinishlarini import qilish
from app.core.admin import UserAdmin, VacancyAdmin, ApplyAdmin

app = FastAPI(
    title="Jobify API",
    description="Ish topish platformasi uchun backend tizimi",
    version="1.0.0",
)

# CORS sozlamalari
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static fayllar uchun papkalar
os.makedirs("uploads/resumes", exist_ok=True)
os.makedirs("uploads/avatars", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Jadvallarni avtomatik yaratish (Bu qolishi shart)
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Admin panelni sozlash
admin = Admin(app, engine)
admin.add_view(UserAdmin)
admin.add_view(VacancyAdmin)
admin.add_view(ApplyAdmin)

# --- Routerlarni ulash (PREFIX OLIB TASHLANDI) ---
app.include_router(auth_router)
app.include_router(profile_router)
app.include_router(vacancy_router)
app.include_router(apply_router)

@app.get("/", tags=["Root"])
async def root():
    return {
        "success": True,
        "message": "Jobify API muvaffaqiyatli ishlayapti! 🚀",
        "docs": "/docs"
    }