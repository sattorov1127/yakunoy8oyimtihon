from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from app.database import get_db
from app.auth.models import User
from app.core.enums import UserRole
from app.core.tasks import send_registration_email
from app.auth.schema import (
    RegisterSchema,
    LoginSchema,
    TokenSchema,
    ChangePasswordSchema,
    UserResponseSchema
)
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token
)

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserResponseSchema)
async def register(data: RegisterSchema, db: AsyncSession = Depends(get_db)):

    if data.role == UserRole.ADMIN:
        raise HTTPException(403, "Admin roli register orqali yaratib bo'lmaydi!")

    if not data.email and not data.phone:
        raise HTTPException(400, "Email yoki telefon raqam kiritilishi shart!")

    if data.email:
        result = await db.execute(select(User).where(User.email == data.email))
        if result.scalar_one_or_none():
            raise HTTPException(400, "Bu email allaqachon ro'yxatdan o'tgan!")

    if data.phone:
        result = await db.execute(select(User).where(User.phone == data.phone))
        if result.scalar_one_or_none():
            raise HTTPException(400, "Bu telefon raqam allaqachon ro'yxatdan o'tgan!")

    new_user = User(
        email=data.email,
        phone=data.phone,
        password=hash_password(data.password),
        role=data.role
    )
    db.add(new_user)
    await db.commit()
    # send_registration_email.delay(new_user.email)
    await db.refresh(new_user)
    return new_user


@router.post("/login", response_model=TokenSchema)
async def login(data: LoginSchema, db: AsyncSession = Depends(get_db)):

    user = None
    if data.email:
        result = await db.execute(select(User).where(User.email == data.email))
        user = result.scalar_one_or_none()
    elif data.phone:
        result = await db.execute(select(User).where(User.phone == data.phone))
        user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(401, "Foydalanuvchi topilmadi!")

    if not verify_password(data.password, user.password):
        raise HTTPException(401, "Parol noto'g'ri!")

    if not user.is_active:
        raise HTTPException(403, "Akkaunt bloklangan!")

    access_token = create_access_token({"sub": str(user.id), "role": user.role})
    refresh_token = create_refresh_token({"sub": str(user.id)})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/refresh", response_model=TokenSchema)
async def refresh(
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db)
):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Token kiritilmagan!")

    token = authorization.split(" ")[1]
    payload = decode_token(token)

    if not payload or payload.get("type") != "refresh":
        raise HTTPException(401, "Token noto'g'ri yoki muddati o'tgan!")

    user_id = payload.get("sub")
    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(401, "Foydalanuvchi topilmadi!")

    access_token = create_access_token({"sub": str(user.id), "role": user.role})
    refresh_token = create_refresh_token({"sub": str(user.id)})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.get("/me", response_model=UserResponseSchema)
async def get_me(
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db)
):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Token kiritilmagan!")

    token = authorization.split(" ")[1]
    payload = decode_token(token)

    if not payload or payload.get("type") != "access":
        raise HTTPException(401, "Token noto'g'ri!")

    user_id = payload.get("sub")
    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(404, "Foydalanuvchi topilmadi!")

    return user


@router.put("/change-password")
async def change_password(data: ChangePasswordSchema,authorization: Optional[str] = Header(None),db: AsyncSession = Depends(get_db)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Token kiritilmagan!")

    token = authorization.split(" ")[1]
    payload = decode_token(token)

    if not payload:
        raise HTTPException(401, "Token noto'g'ri!")

    user_id = payload.get("sub")
    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(404, "Foydalanuvchi topilmadi!")

    if not verify_password(data.old_password, user.password):
        raise HTTPException(400, "Eski parol noto'g'ri!")

    user.password = hash_password(data.new_password)
    await db.commit()

    return {"message": "Parol muvaffaqiyatli o'zgartirildi!"}