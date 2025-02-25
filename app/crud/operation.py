from sqlalchemy.orm import Session

from app.models import OperationOutput, Project


class OperationCrud:
    @staticmethod
    def create(db: Session, file: OperationOutput) -> OperationOutput:
        db.add(file)
        db.commit()
        db.refresh(file)
        return file

    @staticmethod
    def get(db: Session, _id: int) -> OperationOutput | None:
        return db.query(OperationOutput).filter(OperationOutput.id == _id).first()

    @staticmethod
    def get_by_name(db: Session, filename: str, project: Project):
        return (db.query(OperationOutput)
                .filter(OperationOutput.filename == filename)
                .filter(OperationOutput.project == project).first())

    @staticmethod
    def get_by_project(db: Session, project: Project):
        return db.query(OperationOutput).filter(OperationOutput.project == project).first()

    @staticmethod
    def update(db: Session, file: OperationOutput):
        db.merge(file)
        db.commit()
        db.refresh(file)
        return file
