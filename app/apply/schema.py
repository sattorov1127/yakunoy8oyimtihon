from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime
from app.core.enums import ApplyStatus

class ApiResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None

class ResumeResponse(BaseModel):
    id: int
    user_id: int
    title: str
    file_path: str
    created_at: datetime

    class Config:
        from_attributes = True

class ApplyCreate(BaseModel):
    vacancy_id: int
    resume_id: int
    cover_letter: Optional[str] = None

class ApplyResponse(BaseModel):
    id: int
    user_id: int
    vacancy_id: int
    resume_id: int
    cover_letter: Optional[str] = None
    status: ApplyStatus
    created_at: datetime

    class Config:
        from_attributes = True




class ApplyStatusUpdate(BaseModel):
    status: ApplyStatus

class ApplyDetailResponse(BaseModel):
    id: int
    user_id: int
    vacancy_id: int
    resume_id: int
    status: ApplyStatus
    cover_letter: Optional[str]
    created_at: datetime
    candidate_email: Optional[str] = None
    vacancy_title: Optional[str] = None

    class Config:
        from_attributes = True




class NotificationResponse(BaseModel):
    id: int
    user_id: int
    title: str
    message: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True




class FavoriteResponse(BaseModel):
    id: int
    user_id: int
    vacancy_id: int
    created_at: datetime
    vacancy_title: Optional[str] = None

    class Config:
        from_attributes = True