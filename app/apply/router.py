from fastapi import APIRouter, Depends, HTTPException, Header, UploadFile, File, Form, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import Optional
import os, uuid, aiofiles
from datetime import datetime

from app.database import get_db
from app.auth.models import User
from app.vacancy.models import Vacancy
from app.apply.models import Resume, Apply
from app.apply.schema import ApiResponse, ResumeResponse, ApplyCreate, ApplyResponse,ApplyDetailResponse,ApplyStatusUpdate,NotificationResponse,FavoriteResponse
from app.core.security import decode_token
from app.core.enums import UserRole, ApplyStatus

router = APIRouter(prefix="/apply", tags=["Apply & Resume"])


async def get_current_user(authorization: Optional[str] = Header(None), db: AsyncSession = Depends(get_db)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token kiritilmagan!")

    token = authorization.split(" ")[1]
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token yaroqsiz!")

    user_id = payload.get("sub")
    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Foydalanuvchi topilmadi!")
    return user


@router.post("/resume/upload", response_model=ApiResponse)
async def upload_resume(
        title: str = Form(...),
        file: UploadFile = File(...),
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    if current_user.role != UserRole.CANDIDATE:
        return {"success": False, "message": "Faqat nomzodlar rezyume yuklay oladi!", "data": None}

    if file.content_type != "application/pdf":
        return {"success": False, "message": "Faqat PDF formatida yuklang!", "data": None}

    contents = await file.read()
    if len(contents) > 5 * 1024 * 1024:
        return {"success": False, "message": "Fayl hajmi 5MB dan oshmasligi kerak!", "data": None}

    os.makedirs("uploads/resumes", exist_ok=True)
    file_ext = ".pdf"
    filename = f"{uuid.uuid4()}{file_ext}"
    file_path = f"uploads/resumes/{filename}"

    async with aiofiles.open(file_path, "wb") as f:
        await f.write(contents)

    new_resume = Resume(
        user_id=current_user.id,
        title=title,
        file_path=f"/{file_path}"
    )
    db.add(new_resume)
    await db.commit()
    await db.refresh(new_resume)

    return {
        "success": True,
        "message": "Rezyume muvaffaqiyatli yuklandi!",
        "data": ResumeResponse.model_validate(new_resume)
    }


@router.post("/vacancy", response_model=ApiResponse)
async def create_apply(
        data: ApplyCreate,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    if current_user.role != UserRole.CANDIDATE:
        return {"success": False, "message": "Faqat nomzodlar topshira oladi!", "data": None}

    vac_res = await db.execute(select(Vacancy).where(Vacancy.id == data.vacancy_id))
    vacancy = vac_res.scalar_one_or_none()

    if not vacancy:
        return {"success": False, "message": "Vakansiya topilmadi!", "data": None}

    if vacancy.deadline and vacancy.deadline < datetime.utcnow():
        return {"success": False, "message": "Vakansiya muddati o'tib bo'lgan!", "data": None}

    res_check = await db.execute(
        select(Resume).where(and_(Resume.id == data.resume_id, Resume.user_id == current_user.id))
    )
    if not res_check.scalar_one_or_none():
        return {"success": False, "message": "Noto'g'ri rezyume tanlandi!", "data": None}

    dup_check = await db.execute(
        select(Apply).where(and_(Apply.user_id == current_user.id, Apply.vacancy_id == data.vacancy_id))
    )
    if dup_check.scalar_one_or_none():
        return {"success": False, "message": "Siz bu vakansiyaga topshirib bo'lgansiz!", "data": None}

    new_apply = Apply(
        user_id=current_user.id,
        vacancy_id=data.vacancy_id,
        resume_id=data.resume_id,
        cover_letter=data.cover_letter,
        status=ApplyStatus.PENDING
    )
    db.add(new_apply)
    await db.commit()
    await db.refresh(new_apply)
    await send_notification(
        db,
        user_id=vacancy.user_id,
        title="Yangi ariza",
        message=f"'{vacancy.title}' vakansiyasiga yangi ariza kelib tushdi."
    )

    return {
        "success": True,
        "message": "Arizangiz muvaffaqiyatli qabul qilindi!",
        "data": ApplyResponse.model_validate(new_apply)
    }


from app.apply.models import Notification

async def send_notification(db: AsyncSession, user_id: int, title: str, message: str):
    notification = Notification(
        user_id=user_id,
        title=title,
        message=message
    )
    db.add(notification)
    await db.commit()

@router.get("/hr/list", response_model=ApiResponse)
async def get_hr_applications(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    if current_user.role != UserRole.HR:
        return {"success": False, "message": "Bu sahifa faqat HRlar uchun!", "data": None}

    query = (
        select(Apply, Vacancy.title, User.email)
        .join(Vacancy, Apply.vacancy_id == Vacancy.id)
        .join(User, Apply.user_id == User.id)
        .where(Vacancy.user_id == current_user.id)
    )

    result = await db.execute(query)
    rows = result.all()

    applications = []
    for apply_obj, v_title, u_email in rows:
        item = ApplyDetailResponse.model_validate(apply_obj)
        item.vacancy_title = v_title
        item.candidate_email = u_email
        applications.append(item)

    return {
        "success": True,
        "message": "Sizning vakansiyalaringizga kelgan arizalar",
        "data": applications
    }


# --- ARIZA STATUSINI O'ZGARTIRISH (ACCEPTED/REJECTED) ---
@router.patch("/hr/status/{apply_id}", response_model=ApiResponse)
async def update_apply_status(
        apply_id: int,
        data: ApplyStatusUpdate,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    if current_user.role != UserRole.HR:
        return {"success": False, "message": "Ruxsat etilmagan!", "data": None}

    query = (
        select(Apply)
        .join(Vacancy, Apply.vacancy_id == Vacancy.id)
        .where(Apply.id == apply_id, Vacancy.user_id == current_user.id)
    )

    result = await db.execute(query)
    apply = result.scalar_one_or_none()

    if not apply:
        return {"success": False, "message": "Ariza topilmadi yoki sizda ruxsat yo'q!", "data": None}

    apply.status = data.status
    await db.commit()
    await db.refresh(apply)

    status_text = "qabul qilindi" if data.status == ApplyStatus.ACCEPTED else "rad etildi"
    await send_notification(
        db,
        user_id=apply.user_id,
        title="Ariza holati yangilandi",
        message=f"Sizning arizangiz '{status_text}'."
    )

    return {
        "success": True,
        "message": f"Ariza holati '{data.status}'ga o'zgartirildi!",
        "data": ApplyResponse.model_validate(apply)
    }




@router.get("/notifications", response_model=ApiResponse)
async def get_my_notifications(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Notification)
        .where(Notification.user_id == current_user.id)
        .order_by(Notification.created_at.desc())
    )
    notifications = result.scalars().all()

    return {
        "success": True,
        "message": "Bildirishnomalar ro'yxati",
        "data": [NotificationResponse.model_validate(n) for n in notifications]
    }


@router.patch("/notifications/read-all", response_model=ApiResponse)
async def mark_notifications_as_read(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    # O'qilmagan barcha xabarlarni o'qilgan deb belgilash
    from sqlalchemy import update
    await db.execute(
        update(Notification)
        .where(Notification.user_id == current_user.id, Notification.is_read == False)
        .values(is_read=True)
    )
    await db.commit()

    return {"success": True, "message": "Barcha xabarlar o'qildi deb belgilandi", "data": None}


from app.apply.models import Favorite


# ---  VAKANSIYANI SARALANGANLARGA QO'SHISH ---
@router.post("/favorite/{vacancy_id}", response_model=ApiResponse)
async def add_to_favorites(
        vacancy_id: int,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    if current_user.role != UserRole.CANDIDATE:
        return {"success": False, "message": "Faqat nomzodlar vakansiyalarni saqlay oladi!", "data": None}

    vac_res = await db.execute(select(Vacancy).where(Vacancy.id == vacancy_id))
    if not vac_res.scalar_one_or_none():
        return {"success": False, "message": "Vakansiya topilmadi!", "data": None}

    fav_check = await db.execute(
        select(Favorite).where(Favorite.user_id == current_user.id, Favorite.vacancy_id == vacancy_id)
    )
    if fav_check.scalar_one_or_none():
        return {"success": False, "message": "Bu vakansiya allaqachon saralanganlar ro'yxatida!", "data": None}

    new_favorite = Favorite(user_id=current_user.id, vacancy_id=vacancy_id)
    db.add(new_favorite)
    await db.commit()
    await db.refresh(new_favorite)

    return {
        "success": True,
        "message": "Vakansiya saralanganlarga qo'shildi!",
        "data": FavoriteResponse.model_validate(new_favorite)
    }


# ---  SARALANGANLAR RO'YXATINI KO'RISH ---
@router.get("/favorite/my-list", response_model=ApiResponse)
async def get_my_favorites(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    query = (
        select(Favorite, Vacancy.title)
        .join(Vacancy, Favorite.vacancy_id == Vacancy.id)
        .where(Favorite.user_id == current_user.id)
    )

    result = await db.execute(query)
    rows = result.all()

    favorites = []
    for fav_obj, v_title in rows:
        item = FavoriteResponse.model_validate(fav_obj)
        item.vacancy_title = v_title
        favorites.append(item)

    return {
        "success": True,
        "message": "Sizning saralangan vakansiyalaringiz",
        "data": favorites
    }


# ---  SARALANGANLARDAN O'CHIRISH ---
@router.delete("/favorite/{favorite_id}", response_model=ApiResponse)
async def remove_from_favorites(
        favorite_id: int,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Favorite).where(Favorite.id == favorite_id, Favorite.user_id == current_user.id)
    )
    favorite = result.scalar_one_or_none()

    if not favorite:
        return {"success": False, "message": "Ma'lumot topilmadi!", "data": None}

    await db.delete(favorite)
    await db.commit()

    return {"success": True, "message": "Vakansiya saralanganlardan olib tashlandi!", "data": None}