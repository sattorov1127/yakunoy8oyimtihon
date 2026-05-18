from sqladmin import ModelView
from app.auth.models import User
from app.vacancy.models import Vacancy
from app.apply.models import Apply

class UserAdmin(ModelView, model=User):
    # Ustun nomlarini string ko'rinishida yozamiz
    column_list = ["id", "email", "role", "is_active"]
    column_searchable_list = ["email"]
    icon = "fa-solid fa-user"
    name = "Foydalanuvchi"
    name_plural = "Foydalanuvchilar"

class VacancyAdmin(ModelView, model=Vacancy):
    column_list = ["id", "title", "status", "created_at"]
    # Filtrlar uchun ham faqat string ishlating
    # column_filters = ["status"] 
    icon = "fa-solid fa-briefcase"
    name = "Vakansiya"
    name_plural = "Vakansiyalar"

class ApplyAdmin(ModelView, model=Apply):
    column_list = ["id", "status", "created_at"]
    icon = "fa-solid fa-file-signature"
    name = "Ariza"
    name_plural = "Arizalar"