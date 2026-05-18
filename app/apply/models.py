from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Enum as SAEnum,Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base
from app.core.enums import ApplyStatus

class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(300), nullable=False)
    file_path = Column(String(500), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="resumes")
    applies = relationship("Apply", back_populates="resume")


class Apply(Base):
    __tablename__ = "applies"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    vacancy_id = Column(Integer, ForeignKey("vacancies.id"), nullable=False)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=True)
    cover_letter = Column(Text, nullable=True)
    status = Column(SAEnum(ApplyStatus), default=ApplyStatus.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="applies")
    vacancy = relationship("Vacancy", back_populates="applies")
    resume = relationship("Resume", back_populates="applies")


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(300), nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="notifications")


class Favorite(Base):
    __tablename__ = "favorites"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    vacancy_id = Column(Integer, ForeignKey("vacancies.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="favorites")
    vacancy = relationship("Vacancy", back_populates="favorites")