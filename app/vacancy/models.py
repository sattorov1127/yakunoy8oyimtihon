from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Enum as SAEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base
from app.core.enums import VacancyStatus, ExperienceLevel, EmploymentType


class Vacancy(Base):
    __tablename__ = "vacancies"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(300), nullable=False)
    description = Column(Text, nullable=False)
    requirements = Column(Text, nullable=True)
    salary_min = Column(Integer, nullable=True)
    salary_max = Column(Integer, nullable=True)
    location = Column(String(200), nullable=True)
    experience_level = Column(SAEnum(ExperienceLevel), default=ExperienceLevel.NO_EXPERIENCE)
    employment_type = Column(SAEnum(EmploymentType), default=EmploymentType.FULL_TIME)
    status = Column(SAEnum(VacancyStatus), default=VacancyStatus.ACTIVE)
    deadline = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="vacancies")
    applies = relationship("Apply", back_populates="vacancy")
    favorites = relationship("Favorite", back_populates="vacancy")