from fastapi import APIRouter, Depends, HTTPException, Header, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
import os, uuid, aiofiles
from app.database import get_db
from app.auth.models import User
from app.profile.models import CandidateProfile, CompanyProfile
from app.profile.schema import (
    CandidateProfileCreate,
    CandidateProfileResponse,
    CompanyProfileCreate,
    CompanyProfileResponse
)
from app.core.security import decode_token
from app.core.enums import UserRole

router = APIRouter(prefix="/profile", tags=["Profile"])


async def get_current_user(authorization: Optional[str] = Header(None),db: AsyncSession = Depends(get_db)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail={
                "success": False,
                "message": "Token kiritilmagan!",
                "data": None
            }
        )

    token = authorization.split(" ")[1]
    payload = decode_token(token)

    if not payload or payload.get("type") != "access":
        raise HTTPException(
            status_code=401,
            detail={
                "success": False,
                "message": "Token noto'g'ri yoki muddati o'tgan!",
                "data": None
            }
        )

    user_id = payload.get("sub")
    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=404,
            detail={
                "success": False,
                "message": "Foydalanuvchi topilmadi!",
                "data": None
            }
        )

    return user


@router.post("/candidate", status_code=201)
async def create_candidate_profile(data: CandidateProfileCreate, current_user: User = Depends(get_current_user),  db: AsyncSession = Depends(get_db)):
    if current_user.role != UserRole.CANDIDATE:
        raise HTTPException(
            status_code=403,
            detail={
                "success": False,
                "message": "Faqat candidate profil yarata oladi!",
                "data": None
            }
        )

    result = await db.execute(
        select(CandidateProfile).where(CandidateProfile.user_id == current_user.id)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "message": "Profil allaqachon mavjud!",
                "data": None
            }
        )

    profile = CandidateProfile(
        user_id=current_user.id,
        **data.model_dump()
    )
    db.add(profile)
    await db.commit()
    await db.refresh(profile)

    return {
        "success": True,
        "message": "Profil muvaffaqiyatli yaratildi!",
        "data": CandidateProfileResponse.model_validate(profile)
    }


@router.get("/candidate")
async def get_candidate_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(CandidateProfile).where(CandidateProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()

    if not profile:
        raise HTTPException(
            status_code=404,
            detail={
                "success": False,
                "message": "Profil topilmadi!",
                "data": None
            }
        )

    return {
        "success": True,
        "message": "Profil muvaffaqiyatli olindi!",
        "data": CandidateProfileResponse.model_validate(profile)
    }


@router.put("/candidate")
async def update_candidate_profile(
    data: CandidateProfileCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(CandidateProfile).where(CandidateProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()

    if not profile:
        raise HTTPException(
            status_code=404,
            detail={
                "success": False,
                "message": "Profil topilmadi!",
                "data": None
            }
        )

    for key, value in data.model_dump(exclude_none=True).items():
        setattr(profile, key, value)

    await db.commit()
    await db.refresh(profile)

    return {
        "success": True,
        "message": "Profil muvaffaqiyatli yangilandi!",
        "data": CandidateProfileResponse.model_validate(profile)
    }



@router.post("/candidate/avatar")
async def upload_avatar(file: UploadFile = File(...), current_user: User = Depends(get_current_user),db: AsyncSession = Depends(get_db)):
    allowed = ["image/jpeg", "image/png", "image/jpg"]
    if file.content_type not in allowed:
        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "message": "Faqat JPG yoki PNG rasm yuklanadi!",
                "data": None
            }
        )

    contents = await file.read()
    if len(contents) > 2 * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "message": "Rasm hajmi 2MB dan oshmasligi kerak!",
                "data": None
            }
        )

    os.makedirs("uploads/avatars", exist_ok=True)
    filename = f"{uuid.uuid4()}.jpg"
    file_path = f"uploads/avatars/{filename}"

    async with aiofiles.open(file_path, "wb") as f:
        await f.write(contents)

    result = await db.execute(
        select(CandidateProfile).where(CandidateProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()

    if not profile:
        raise HTTPException(
            status_code=404,
            detail={
                "success": False,
                "message": "Avval profil yarating!",
                "data": None
            }
        )

    profile.avatar = f"/uploads/avatars/{filename}"
    await db.commit()

    return {
        "success": True,
        "message": "Avatar muvaffaqiyatli yuklandi!",
        "data": {
            "avatar_url": f"/uploads/avatars/{filename}"
        }
    }


@router.post("/company", status_code=201)
async def create_company_profile(data: CompanyProfileCreate,current_user: User = Depends(get_current_user),db: AsyncSession = Depends(get_db)):
    if current_user.role != UserRole.HR:
        raise HTTPException(
            status_code=403,
            detail={
                "success": False,
                "message": "Faqat HR kompaniya profili yarata oladi!",
                "data": None
            }
        )

    result = await db.execute(select(CompanyProfile).where(CompanyProfile.user_id == current_user.id))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "message": "Kompaniya profili allaqachon mavjud!",
                "data": None
            }
        )

    profile = CompanyProfile(
        user_id=current_user.id,
        **data.model_dump()
    )
    db.add(profile)
    await db.commit()
    await db.refresh(profile)

    return {
        "success": True,
        "message": "Kompaniya profili muvaffaqiyatli yaratildi!",
        "data": CompanyProfileResponse.model_validate(profile)
    }


@router.get("/company")
async def get_company_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(CompanyProfile).where(CompanyProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()

    if not profile:
        raise HTTPException(
            status_code=404,
            detail={
                "success": False,
                "message": "Kompaniya profili topilmadi!",
                "data": None
            }
        )

    return {
        "success": True,
        "message": "Kompaniya profili muvaffaqiyatli olindi!",
        "data": CompanyProfileResponse.model_validate(profile)
    }


@router.put("/company")
async def update_company_profile(
    data: CompanyProfileCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(CompanyProfile).where(CompanyProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()

    if not profile:
        raise HTTPException(
            status_code=404,
            detail={
                "success": False,
                "message": "Kompaniya profili topilmadi!",
                "data": None
            }
        )

    for key, value in data.model_dump(exclude_none=True).items():
        setattr(profile, key, value)

    await db.commit()
    await db.refresh(profile)

    return {
        "success": True,
        "message": "Kompaniya profili muvaffaqiyatli yangilandi!",
        "data": CompanyProfileResponse.model_validate(profile)
    }