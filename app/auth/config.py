from functools import lru_cache

from pydantic import PostgresDsn, field_validator
from pydantic_core.core_schema import FieldValidationInfo
from pydantic_settings import BaseSettings, SettingsConfigDict


class Setting(BaseSettings):
    jwt_algorithm: str = "HS256"
    secret_key: str
    access_token_expire_days: int = 1
    refresh_token_expire_days: int = 7

    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    sqlalchemy_database_url: str | None = None

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

    model_config = SettingsConfigDict(env_file="app/auth/.auth.env")


@lru_cache
def get_setting():
    return Setting()


settings = get_setting()
