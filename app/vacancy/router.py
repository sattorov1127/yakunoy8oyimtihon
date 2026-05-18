from fastapi import APIRouter, Depends, HTTPException, Header, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from typing import Optional
from datetime import datetime
from app.database import get_db
from app.auth.models import User
from app.vacancy.models import Vacancy
from app.vacancy.schema import VacancyCreate, VacancyUpdate, VacancyResponse
from app.core.security import decode_token
from app.core.enums import UserRole, VacancyStatus

router = APIRouter(prefix="/vacancy", tags=["Vacancy"])


# ─── HELPER — Current User ──────────────────────────────
async def get_current_user(authorization: Optional[str] = Header(None), db: AsyncSession = Depends(get_db)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail={"success": False, "message": "Token kiritilmagan!", "data": None}
        )

    token = authorization.split(" ")[1]
    payload = decode_token(token)

    if not payload or payload.get("type") != "access":
        raise HTTPException(
            status_code=401,
            detail={"success": False, "message": "Token noto'g'ri!", "data": None}
        )

    user_id = payload.get("sub")
    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=404,
            detail={"success": False, "message": "Foydalanuvchi topilmadi!", "data": None}
        )
    return user


@router.post("/create", status_code=201)
async def create_vacancy(
    data: VacancyCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if current_user.role != UserRole.HR:
        raise HTTPException(
            status_code=403,
            detail={"success": False, "message": "Faqat HR vacancy yarata oladi!", "data": None}
        )

    if data.deadline and data.deadline < datetime.utcnow():
        raise HTTPException(
            status_code=400,
            detail={"success": False, "message": "Deadline o'tmishda bo'lishi mumkin emas!", "data": None}
        )

    vacancy = Vacancy(
        user_id=current_user.id,
        **data.model_dump()
    )
    db.add(vacancy)
    await db.commit()
    await db.refresh(vacancy)

    return {
        "success": True,
        "message": "Vacancy muvaffaqiyatli yaratildi!",
        "data": VacancyResponse.model_validate(vacancy)
    }


# ─── BARCHA VACANCYLAR — Pagination + Search + Filter ───
@router.get("/list")
async def get_vacancies(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50),
    search: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    employment_type: Optional[str] = Query(None),
    experience_level: Optional[str] = Query(None),
    salary_min: Optional[int] = Query(None),
    salary_max: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    query = select(Vacancy).where(Vacancy.status == VacancyStatus.ACTIVE)

    # Search
    if search:
        query = query.where(
            or_(
                Vacancy.title.ilike(f"%{search}%"),
                Vacancy.description.ilike(f"%{search}%")
            )
        )

    # Filter
    if location:
        query = query.where(Vacancy.location.ilike(f"%{location}%"))

    if employment_type:
        query = query.where(Vacancy.employment_type == employment_type)

    if experience_level:
        query = query.where(Vacancy.experience_level == experience_level)

    if salary_min:
        query = query.where(Vacancy.salary_min >= salary_min)

    if salary_max:
        query = query.where(Vacancy.salary_max <= salary_max)

    # Pagination
    offset = (page - 1) * limit
    query = query.offset(offset).limit(limit)

    result = await db.execute(query)
    vacancies = result.scalars().all()

    return {
        "success": True,
        "message": "Vacancylar muvaffaqiyatli olindi!",
        "data": {
            "page": page,
            "limit": limit,
            "total": len(vacancies),
            "vacancies": [VacancyResponse.model_validate(v) for v in vacancies]
        }
    }


# ─── BITTA VACANCY ──────────────────────────────────────
@router.get("/detail/{vacancy_id}")
async def get_vacancy(
    vacancy_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Vacancy).where(Vacancy.id == vacancy_id))
    vacancy = result.scalar_one_or_none()

    if not vacancy:
        raise HTTPException(
            status_code=404,
            detail={"success": False, "message": "Vacancy topilmadi!", "data": None}
        )

    return {
        "success": True,
        "message": "Vacancy muvaffaqiyatli olindi!",
        "data": VacancyResponse.model_validate(vacancy)
    }


# ─── VACANCY YANGILASH ───────────────────────────────────
@router.put("/update/{vacancy_id}")
async def update_vacancy(
    vacancy_id: int,
    data: VacancyUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Vacancy).where(Vacancy.id == vacancy_id))
    vacancy = result.scalar_one_or_none()

    if not vacancy:
        raise HTTPException(
            status_code=404,
            detail={"success": False, "message": "Vacancy topilmadi!", "data": None}
        )

    if vacancy.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail={"success": False, "message": "Bu vacancyni tahrirlash huquqi yo'q!", "data": None}
        )

    for key, value in data.model_dump(exclude_none=True).items():
        setattr(vacancy, key, value)

    await db.commit()
    await db.refresh(vacancy)

    return {
        "success": True,
        "message": "Vacancy muvaffaqiyatli yangilandi!",
        "data": VacancyResponse.model_validate(vacancy)
    }


# ─── VACANCY O'CHIRISH ───────────────────────────────────
@router.delete("/delete/{vacancy_id}")
async def delete_vacancy(
    vacancy_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Vacancy).where(Vacancy.id == vacancy_id))
    vacancy = result.scalar_one_or_none()

    if not vacancy:
        raise HTTPException(
            status_code=404,
            detail={"success": False, "message": "Vacancy topilmadi!", "data": None}
        )

    if vacancy.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail={"success": False, "message": "Bu vacancyni o'chirish huquqi yo'q!", "data": None}
        )

    await db.delete(vacancy)
    await db.commit()

    return {
        "success": True,
        "message": "Vacancy muvaffaqiyatli o'chirildi!",
        "data": None
    }


# ─── O'Z VACANCYLARI — HR uchun ─────────────────────────
@router.get("/my/list")
async def get_my_vacancies(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if current_user.role != UserRole.HR:
        raise HTTPException(
            status_code=403,
            detail={"success": False, "message": "Faqat HR uchun!", "data": None}
        )

    result = await db.execute(
        select(Vacancy).where(Vacancy.user_id == current_user.id)
    )
    vacancies = result.scalars().all()

    return {
        "success": True,
        "message": "Sizning vacancylaringiz!",
        "data": [VacancyResponse.model_validate(v) for v in vacancies]
    }