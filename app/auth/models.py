from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SAEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base
from app.core.enums import UserRole


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=True)
    phone = Column(String, unique=True, nullable=True)
    password = Column(String, nullable=False)
    role = Column(SAEnum(UserRole), default=UserRole.CANDIDATE, nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


    candidate_profile = relationship("CandidateProfile", back_populates="user", uselist=False)
    company_profile = relationship("CompanyProfile", back_populates="user", uselist=False)
    resumes = relationship("Resume", back_populates="user")
    vacancies = relationship("Vacancy", back_populates="user")
    applies = relationship("Apply", back_populates="user")
    notifications = relationship("Notification", back_populates="user")
    favorites = relationship("Favorite", back_populates="user")