from typing import List
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl, validator


class Settings(BaseSettings):
    APP_NAME: str = "CFM Fittings Pro"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"
    DEBUG: bool = True

    SECRET_KEY: str = "change-this-to-a-very-long-random-secret-key-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    POSTGRES_HOST: str = "cfm_postgres"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "cfm_fittings"
    POSTGRES_USER: str = "cfm_user"
    POSTGRES_PASSWORD: str = "cfm_secure_password_change_in_production"
    DATABASE_URL: str = ""

    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://cfm_frontend:5173",
    ]

    STORAGE_PATH: str = "/app/storage"
    MAX_UPLOAD_SIZE_MB: int = 50

    FIRST_SUPERADMIN_EMAIL: str = "admin@cfmfittings.com"
    FIRST_SUPERADMIN_PASSWORD: str = "Admin@123!ChangeMe"
    FIRST_TENANT_NAME: str = "CFM Default Tenant"

    @validator("DATABASE_URL", pre=True, always=True)
    def build_database_url(cls, v, values):
        if v:
            return v
        return (
            f"postgresql+asyncpg://{values['POSTGRES_USER']}:"
            f"{values['POSTGRES_PASSWORD']}@{values['POSTGRES_HOST']}:"
            f"{values['POSTGRES_PORT']}/{values['POSTGRES_DB']}"
        )

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
