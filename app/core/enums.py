from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    HR = "hr"
    CANDIDATE = "candidate"

class ApplyStatus(str, Enum):
    PENDING = "pending"
    REVIEWED = "reviewed"
    ACCEPTED = "accepted"
    REJECTED = "rejected"

class VacancyStatus(str, Enum):
    ACTIVE = "active"
    CLOSED = "closed"
    DRAFT = "draft"

class ExperienceLevel(str, Enum):
    NO_EXPERIENCE = "no_experience"
    JUNIOR = "junior"
    MIDDLE = "middle"
    SENIOR = "senior"

class EmploymentType(str, Enum):
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    REMOTE = "remote"
    HYBRID = "hybrid"
    INTERNSHIP = "internship"