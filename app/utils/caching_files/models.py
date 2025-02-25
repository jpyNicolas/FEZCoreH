import datetime

from sqlalchemy import UUID, Column, DateTime, Integer

from .database import Base, engine


class File(Base):
    __tablename__ = "files_cache"
    unique_name = Column(UUID, primary_key=True)
    created_at = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc))


class FolderSize(Base):
    __tablename__ = "cache_folder_size"
    size = Column(Integer, primary_key=True, autoincrement=False)


Base.metadata.create_all(bind=engine)
