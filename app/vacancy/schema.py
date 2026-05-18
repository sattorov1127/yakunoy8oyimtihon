from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.core.enums import VacancyStatus, ExperienceLevel, EmploymentType


# ─── CREATE ─────────────────────────────────────────────
class VacancyCreate(BaseModel):
    title: str
    description: str
    requirements: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    location: Optional[str] = None
    experience_level: ExperienceLevel = ExperienceLevel.NO_EXPERIENCE
    employment_type: EmploymentType = EmploymentType.FULL_TIME
    deadline: Optional[datetime] = None

    class Config:
        use_enum_values = True


# ─── UPDATE ─────────────────────────────────────────────
class VacancyUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    requirements: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    location: Optional[str] = None
    experience_level: Optional[ExperienceLevel] = None
    employment_type: Optional[EmploymentType] = None
    status: Optional[VacancyStatus] = None
    deadline: Optional[datetime] = None

    class Config:
        use_enum_values = True


# ─── RESPONSE ───────────────────────────────────────────
class VacancyResponse(BaseModel):
    id: int
    user_id: int
    title: str
    description: str
    requirements: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    location: Optional[str] = None
    experience_level: str
    employment_type: str
    status: str
    deadline: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True