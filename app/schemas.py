from datetime import datetime

from email_validator import validate_email
from fastapi import Form, UploadFile
from pydantic import BaseModel, Field, field_validator
from pydantic import EmailStr as PydanticEmailStr


class EmailStr(PydanticEmailStr):
    @classmethod
    @field_validator("value", mode="before")
    def _validate(cls, value: str) -> str:
        email = validate_email(value).normalized
        return email.lower()


class ApiKeyBase(BaseModel):
    id: int
    name: str


class ApiKey(ApiKeyBase):
    key: str

    class Config:
        from_attributes = True


class UserBase(BaseModel):
    email: EmailStr


class SignInUser(UserBase):
    password: str = Field(min_length=6, max_length=32)


class User(UserBase):
    name: str | None = Field(min_length=2, max_length=32, default=None)


class UserCreate(User):
    password: str = Field(min_length=6, max_length=32)


# class Login(BaseModel):
#     email: EmailStr
#     password: str = Field(max_length=32)


class OTP(BaseModel):
    email: EmailStr
    code: str = Field(max_length=5, default="string")


class Confirm(OTP):
    pass


class RecoveryPassword(Confirm):
    password: str = Field(min_length=6, max_length=32)


class ChangePassword(BaseModel):
    password: str = Field(min_length=6, max_length=32, alias="current_password")
    new_password: str = Field(min_length=6, max_length=32)


class Project(BaseModel):
    name: str = Field(max_length=32)
    description: str | None = Field(max_length=255)

    class Config:
        from_attributes = True


class ProjectFilter(BaseModel):
    name: str | None = Field(max_length=32, default=None)
    description: str | None = Field(max_length=255, default=None)
    created_at: datetime | None = None


class FileSchema(BaseModel):
    file: UploadFile
    filename: str | None
    extension: str


class BandsNamesRequestForm:
    def __init__(
        self,
        red_band: int | None = Form(default=None),
        green_band: int | None = Form(default=None),
        blue_band: int | None = Form(default=None),
        nir_band: int | None = Form(default=None),
        swir1_band: int | None = Form(default=None),
        swir2_band: int | None = Form(default=None),
    ):
        self.bands = {
            "red_band_id": red_band,
            "green_band_id": green_band,
            "blue_band_id": blue_band,
            "nir_band_id": nir_band,
            "swir1_band_id": swir1_band,
            "swir2_band_id": swir2_band,
        }


class Bands(BaseModel):
    red_band: int | None = None
    green_band: int | None = None
    blue_band: int | None = None
    nir_band: int | None = None
    swir1_band: int | None = None
    swir2_band: int | None = None


class BandsTest(BaseModel):
    red_band: int = Form()
    green_band: int = Form()


class ContactUsForm(BaseModel):
    email: EmailStr
    message: str


class NewDemoRequest(BaseModel):
    email: EmailStr
    company_name: str
    message: str | None = None
