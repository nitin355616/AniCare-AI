import os
from typing import List, Union
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator


class Settings(BaseSettings):
    PROJECT_NAME: str = "AniCare AI — Animal Health & Early-Warning Platform"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    API_V1_PREFIX: str = "/api"
    API_V1_STR: str = "/api"

    # Database
    MONGODB_URL: str = Field(default="mongodb://127.0.0.1:27017")
    DATABASE_NAME: str = Field(default="anicare_ai")

    # Security & JWT
    JWT_SECRET_KEY: str = Field(default="anicare_ai_jwt_super_secret_key_sih2026_dev_seed")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    # CORS
    CORS_ORIGINS: Union[str, List[str]] = "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://127.0.0.1:8000,http://localhost:8000"

    # Uploads
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE_MB: int = 10

    # Datasets Configuration & Manifests
    DATASET_FMD_CATTLE_DIR: str = Field(default="backend/datasets/FMD_Cattle")
    DATASET_ARCHIVE_DIR: str = Field(default="backend/datasets/archive")
    DATASET_MUZZLE_DIR: str = Field(default="backend/datasets/Sahiwal_Cattle_Murrah_Buffalo")
    DATASET_SPECIES_DIR: str = Field(default="backend/datasets/Class3_Image_Data")
    DATASET_TEST_DIR: str = Field(default="backend/datasets/External_Test_Data/test")
    DATASETS_MANIFEST_DIR: str = Field(default="backend/ai/manifests")

    @field_validator("CORS_ORIGINS", mode="after")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    @property
    def cors_origins_list(self) -> List[str]:
        if isinstance(self.CORS_ORIGINS, list):
            return self.CORS_ORIGINS
        return [o.strip() for o in str(self.CORS_ORIGINS).split(",") if o.strip()]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()
