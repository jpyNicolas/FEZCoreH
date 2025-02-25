from sqlalchemy.orm import Session

from app.models import Project, User


class ProjectCrud:
    @staticmethod
    def create(db: Session, project: Project) -> Project:
        db.add(project)
        db.commit()
        db.refresh(project)
        return project

    @staticmethod
    def get(db: Session, _id: int, user: User) -> Project | None:
        return (
            db.query(Project)
            .filter(Project.id == _id)
            .filter(Project.user == user)
            .first()
        )

    @staticmethod
    def get_by_name(db: Session, name: str, user: User) -> Project | None:
        return (
            db.query(Project)
            .filter(Project.name == name)
            .filter(Project.user == user)
            .first()
        )

    @staticmethod
    def get_all(db: Session, user: User, skip: int = 0, limit: int = 100):
        return (
            db.query(Project)
            .filter(Project.user == user)
            .filter(Project.deleted_at == None)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_filter(
        db: Session,
        user: User,
        skip: int = 0,
        limit: int = 100,
        name: str = "",
        description: str = "",
    ):
        return (
            db.query(Project)
            .filter(Project.user == user)
            .filter(Project.deleted_at == None)
            .filter(Project.name.like(f"%{name}%"))
            .filter(Project.description.like(f"%{description}%"))
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def update(db: Session, project: Project) -> Project:
        project = db.merge(project)
        db.commit()
        db.refresh(project)
        return project
