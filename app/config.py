from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/jobify"
    SECRET_KEY: str = "jobify-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    MAX_FILE_SIZE: int = 5 * 1024 * 1024
    UPLOAD_DIR: str = "uploads"

    class Config:
        env_file = ".env"

settings = Settings()