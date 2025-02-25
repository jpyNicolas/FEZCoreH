import enum
from datetime import datetime

from sqlalchemy import UUID, BigInteger, Boolean, Enum, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class UserRole(enum.Enum):
    premium = "premium"
    user = "user"


class SavedLocationType(enum.Enum):
    external = "external"
    internal = "internal"


class TimeMixin:
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        default=func.now(),
        onupdate=func.now(),
    )
    deleted_at: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=True)


class User(Base, TimeMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String)
    name: Mapped[str] = mapped_column(String)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.user)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    is_banned: Mapped[bool] = mapped_column(Boolean, default=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)

    api_keys: Mapped[list["ApiKey"]] = relationship("ApiKey", back_populates="user")
    projects: Mapped[list["Project"]] = relationship("Project", back_populates="user")


class Admin(Base, TimeMixin):
    __tablename__ = "admins"

    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id"), primary_key=True
    )


class ApiKey(Base, TimeMixin):
    __tablename__ = "api_keys"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String)
    key: Mapped[str] = mapped_column(String, unique=True, index=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"))

    user: Mapped[User] = relationship("User", back_populates="api_keys")


class Project(Base, TimeMixin):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50))
    description: Mapped[str] = mapped_column(String(255), nullable=True)
    last_action: Mapped[str] = mapped_column(String(255), nullable=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"))

    user: Mapped[User] = relationship("User", back_populates="projects")
    files: Mapped[list["File"]] = relationship(
        "File", back_populates="project", cascade="all, delete-orphan"
    )
    operation_output: Mapped[list["operation_output"]] = relationship(
        "OperationOutput", back_populates="project", cascade="all, delete-orphan"
    )


class File(Base, TimeMixin):
    __tablename__ = "files"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    filename: Mapped[str] = mapped_column(String(100))
    unique_name: Mapped[UUID] = mapped_column(UUID(as_uuid=True), unique=True)
    extension: Mapped[str] = mapped_column(String(10))

    project_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("projects.id"),
        nullable=False,
    )
    location_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("saved_locations.id"), nullable=True
    )

    project: Mapped[Project] = relationship("Project", back_populates="files")
    location: Mapped["SavedLocation"] = relationship(
        "SavedLocation", back_populates="files"
    )


class OperationOutput(Base, TimeMixin):
    __tablename__ = "operation_output"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    title: Mapped[str] = mapped_column(String(255), unique=False)
    unique_name: Mapped[UUID] = mapped_column(UUID(as_uuid=True), unique=True)
    extension: Mapped[str] = mapped_column(String(10))

    project_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("projects.id"))
    location_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("saved_locations.id"), nullable=True
    )

    project: Mapped[Project] = relationship(
        "Project", back_populates="operation_output"
    )
    location: Mapped["SavedLocation"] = relationship("SavedLocation")


class SavedLocation(Base, TimeMixin):
    __tablename__ = "saved_locations"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    location: Mapped[str] = mapped_column(String)
    endpoint: Mapped[str] = mapped_column(String, nullable=True)
    access_key: Mapped[str] = mapped_column(String, nullable=True)
    secret_key: Mapped[str] = mapped_column(String, nullable=True)
    bucket_name: Mapped[str] = mapped_column(String, nullable=True)
    type: Mapped[SavedLocationType] = mapped_column(Enum(SavedLocationType))
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)

    files: Mapped[list[File]] = relationship("File", back_populates="location")


class OTP(Base, TimeMixin):
    __tablename__ = "otp"

    email: Mapped[str] = mapped_column(String, primary_key=True)
    code: Mapped[int] = mapped_column(String(10))


class ResetPasswordOTP(Base, TimeMixin):
    __tablename__ = "reset_password_otp"

    email: Mapped[str] = mapped_column(String, primary_key=True)
    code: Mapped[str] = mapped_column(String(10))


class DemoRequest(Base, TimeMixin):
    __tablename__ = "demo_requests"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String, unique=True)
    company_name: Mapped[str] = mapped_column(String)
    message: Mapped[str] = mapped_column(String, nullable=True)
    approved: Mapped[bool] = mapped_column(Boolean, nullable=True)
    key: Mapped[str] = mapped_column(String, nullable=True)
    expired_key: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=True)
