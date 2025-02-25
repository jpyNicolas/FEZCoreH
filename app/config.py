from functools import lru_cache

from pydantic import PostgresDsn, field_validator, computed_field
from pydantic_core.core_schema import FieldValidationInfo
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    sqlalchemy_database_url: str | None = None
    ENV_MODE: str

    @field_validator("sqlalchemy_database_url", mode="before")
    @classmethod
    def assemble_db_uri(cls, field_value, info: FieldValidationInfo) -> str:
        if isinstance(field_value, str):
            return field_value
        return PostgresDsn.build(
            scheme="postgresql+psycopg2",
            username=info.data.get("POSTGRES_USER"),
            password=info.data.get("POSTGRES_PASSWORD"),
            host=info.data.get("POSTGRES_SERVER"),
            path=info.data.get("POSTGRES_DB") or "",
        ).unicode_string()

    smtp_user: str | None = None
    smtp_password: str | None = None
    smtp_server: str | None = "localhost"
    smtp_port: int | None = None
    mail_from: str | None = None

    OBJECT_STORAGE_ENDPOINT: str
    OBJECT_STORAGE_ACCESS_KEY: str
    OBJECT_STORAGE_SECRET_KEY: str
    OBJECT_STORAGE_BUCKET_NAME: str
    OBJECT_STORAGE_URL: str

    cache_folder: str | None = None
    max_cache_folder_size: int = 10  # In GB
    local_save_files: str

    @computed_field(return_type=bool)
    @property
    def cache_file_enabled(self):
        return bool(self.cache_folder)

    max_size_file: int = 5 * (10**7)
    max_size_file_premium: int = 2 * (10**8)

    model_config = SettingsConfigDict(env_file="./.env" , extra='allow')


@lru_cache
def get_settings():
    return Settings()


settings: Settings = get_settings()
