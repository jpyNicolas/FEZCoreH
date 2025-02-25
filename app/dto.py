from datetime import datetime
from typing import Any, Optional

from email_validator import validate_email
from pydantic import UUID4, BaseModel, computed_field, field_validator
from pydantic import EmailStr as PydanticEmailStr

from app import schemas
from app.config import settings


class EmailStr(PydanticEmailStr):
    @classmethod
    @field_validator("value", mode="before")
    def _validate(cls, value: str) -> str:
        email = validate_email(value).normalized
        return email.lower()


class File(BaseModel):
    id: int
    filename: str
    unique_name: UUID4
    extension: str

    @computed_field(return_type=str)
    def thumbnail_path(self):
        if settings.ENV_MODE == "production":
            return f"https://core.feztool.com/static/images/thumbnails/{self.unique_name}.png"
        else:
            return (
                f"http://localhost:8000/static/images/thumbnails/{self.unique_name}.png"
            )

    @computed_field(return_type=str)
    def image_path(self):
        if settings.ENV_MODE == "production":
            return f"https://core.feztool.com/static/images/{self.unique_name}.png"
        else:
            return f"http://localhost:8000/static/images/{self.unique_name}.png"

    @computed_field(return_type=str)
    def file_path(self):
        return f"{settings.OBJECT_STORAGE_URL}/{str(self.unique_name)}.{self.extension}"

    class Config:
        from_attributes = True


class OperationOutput(BaseModel):
    id: int
    unique_name: UUID4
    title: str
    extension: str

    @computed_field(return_type=str)
    def image_path(self):
        if settings.ENV_MODE == "production":
            return f"https://core.feztool.com/static/images/{self.unique_name}.{self.extension}"
        else:
            return f"http://localhost:8000/static/images/{self.unique_name}.{self.extension}"

    @computed_field(return_type=str)
    def file_path(self):
        return f"{settings.OBJECT_STORAGE_URL}/{str(self.unique_name)}.{self.extension}"

    class Config:
        from_attributes = True


class Project(schemas.Project):
    id: int
    created_at: datetime
    updated_at: datetime
    files: list[File]
    operation_output: list[OperationOutput]
    tag: str = "Remote sensing"
    subtitle: Optional[str] = None
    last_action: Optional[str] = None


class ApiKey(schemas.ApiKeyBase):
    key: str


class ShowApiKey(schemas.ApiKeyBase):
    pass


class ApiKeyCreationResponse(ApiKey):
    pass


class ShowUser(schemas.User):
    id: int
    role: Any
    created_at: datetime
    updated_at: datetime
    api_keys: list[ShowApiKey] | None


class DemoRequestInfo(BaseModel):
    id: int
    email: EmailStr
    company_name: str
    message: str


class DemoRequestSingle(DemoRequestInfo):
    approved: bool | None = None
    key: str | None = None
    expired_key: datetime | None = None
    created_at: datetime
    updated_at: datetime | None = None
    deleted_at: datetime | None = None
