from sqlalchemy.orm import Session

from app.models import Admin, User


class USERCrud:

    @staticmethod
    def create(db: Session, user: User) -> User:
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def get_by_email(db: Session, email: str) -> User:
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def get_by_id(db: Session, user_id: int) -> User:
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def update(db: Session, user: User) -> User:
        user = db.merge(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def get_admin_by_id(db: Session, id: int) -> Admin:
        return db.query(Admin).filter(Admin.user_id == id).first()
