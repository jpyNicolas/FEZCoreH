from functools import lru_cache
from pathlib import Path

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.config import settings
from .crud import FileCrud, FolderSizeCrud
from .database import session
from .models import File


@lru_cache
def get_folder_size(folder) -> int:
    cache_folder_path = Path(settings.cache_folder)
    cache_folder_path.mkdir(parents=True, exist_ok=True)
    size = sum(file.stat().st_size for file in Path(folder).rglob('*'))
    return size


@lru_cache
def _insert_folder_size(db: Session):
    FolderSizeCrud.create(db, get_folder_size(settings.cache_folder))


_insert_folder_size(session)


def _sync_files_in_db(db: Session):
    filenames = [file.name.rsplit(".", 1)[0] for file in Path(settings.cache_folder).iterdir()]
    for filename in filenames:
        file = FileCrud.get(db, filename)
        if not file:
            FileCrud.create(db, filename)
    db_files = FileCrud.get_all(db)
    for file in db_files:
        if str(file.unique_name) not in filenames:
            FileCrud.delete(db, file.unique_name)


_sync_files_in_db(session)


class FullyCacheFolderException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message


class Cache:
    def __init__(self, db: Session = session):
        self.db = db

    def save(self, file: UploadFile, unique_name: str, prefix: str):
        current_size_gb = FolderSizeCrud.get(self.db).size / (1024 ** 3)
        file_content = file.file.read()
        file_size_gb = len(file_content) / (1024 ** 3)

        if current_size_gb + file_size_gb < settings.max_cache_folder_size:
            try:
                file.file.seek(0)
                cache_folder_path = Path(settings.cache_folder)

                file_path = cache_folder_path / f"{unique_name}.{prefix}"

                with open(file_path, "wb") as f:
                    f.write(file_content)
                file_size = file_size_gb * (1024 ** 3)
                FolderSizeCrud.add(self.db, file_size)
                FileCrud.create(self.db, unique_name)
            except Exception as e:
                raise e
            finally:
                file.file.seek(0)
        else:
            raise FullyCacheFolderException("Cache folder size is full")

    def get(self, unique_name: str) -> File | None:
        return FileCrud.get(self.db, unique_name)
