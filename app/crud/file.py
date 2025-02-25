from datetime import datetime

from sqlalchemy.orm import Session

from app.models import File, Project


class FileCrud:
    @staticmethod
    def create(db: Session, file: File):
        db.add(file)
        db.commit()
        db.refresh(file)
        return file

    @staticmethod
    def get(db: Session, _id: int, project: Project) -> File | None:
        return (
            db.query(File)
            .filter(File.id == _id)
            .filter(File.project == project)
            .first()
        )

    @staticmethod
    def get_by_id(db: Session, _id: int) -> File | None:
        return db.query(File).filter(File.id == _id).first()

    @staticmethod
    def get_by_unique_name(db: Session, unique_name: str) -> File | None:
        return db.query(File).filter(File.unique_name == unique_name).first()

    @staticmethod
    def get_by_name(db: Session, filename: str, project: Project) -> File | None:
        return (
            db.query(File)
            .filter(File.filename == filename)
            .filter(File.project_id == project.id)
            .first()
        )

    @staticmethod
    def get_all_files_in_project(db: Session, project: Project) -> list[File]:
        return db.query(File).filter(File.project == project).all()

    @staticmethod
    def update(db: Session, file: File):
        file = db.merge(file)
        db.commit()
        db.refresh(file)
        return file

    @staticmethod
    def delete(db: Session, unique_name: str):
        file = FileCrud.get_by_unique_name(db, unique_name)
        if file:
            db.delete(file)
            db.commit()

    @staticmethod
    def soft_delete(db: Session, _id: int):
        file = FileCrud.get_by_id(db, _id)
        if file:
            file.deleted_at = datetime.now()
            file = db.merge(file)
            db.commit()
            db.refresh(file)
            return file
