from sqlalchemy.orm import Session

from .models import File, FolderSize


class FileCrud:
    @staticmethod
    def create(db: Session, unique_name: str)-> File:
        file_model = File(unique_name=unique_name)
        db.add(file_model)
        db.commit()
        db.refresh(file_model)
        return file_model

    @staticmethod
    def get(db: Session, unique_name: str) -> File | None:
        return db.query(File).filter(File.unique_name == unique_name).first()

    @staticmethod
    def get_all(db: Session) -> list[File]:
        return db.query(File).all()

    @staticmethod
    def delete(db: Session, unique_name: str) -> File:
        file_model = db.query(File).filter(File.unique_name == unique_name).first()
        if file_model:
            db.delete(file_model)
            db.commit()
        return file_model


class FolderSizeCrud:

    @staticmethod
    def _get_existing_record(db: Session) -> FolderSize | None:
        return db.query(FolderSize).first()

    @staticmethod
    def add(db: Session, size: int):
        existing_record = FolderSizeCrud._get_existing_record(db)
        if existing_record:
            existing_record.size += size
            db.merge(existing_record)
        else:
            new_size = FolderSize(size=size)
            db.add(new_size)
        db.commit()

    @staticmethod
    def create(db: Session, size):
        existing_record = FolderSizeCrud._get_existing_record(db)
        if existing_record:
            existing_record.size = size
            db.merge(existing_record)
        else:
            new_size = FolderSize(size=size)
            db.add(new_size)
        db.commit()

    @staticmethod
    def get(db: Session):
        return db.query(FolderSize).first()
