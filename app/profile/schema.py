from pydantic import BaseModel
from typing import Optional


class CandidateProfileCreate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    bio: Optional[str] = None
    skills: Optional[str] = None
    location: Optional[str] = None


class CandidateProfileResponse(BaseModel):
    id: int
    user_id: int
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    bio: Optional[str] = None
    skills: Optional[str] = None
    location: Optional[str] = None
    avatar: Optional[str] = None

    class Config:
        from_attributes = True


class CompanyProfileCreate(BaseModel):
    company_name: str
    description: Optional[str] = None
    website: Optional[str] = None
    location: Optional[str] = None


class CompanyProfileResponse(BaseModel):
    id: int
    user_id: int
    company_name: str
    description: Optional[str] = None
    website: Optional[str] = None
    location: Optional[str] = None
    logo: Optional[str] = None

    class Config:
        from_attributes = True