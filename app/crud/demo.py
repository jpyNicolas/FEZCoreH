from sqlalchemy.orm import Session

from app.models import DemoRequest


class DemoRequestCRUD:
    @staticmethod
    def get_demo_by_email(db: Session, email: str) -> DemoRequest | None:
        return db.query(DemoRequest).filter(DemoRequest.email == email).first()

    @staticmethod
    def get_demo_signin(db: Session, email: str) -> DemoRequest | None:
        return db.query(DemoRequest).filter(DemoRequest.email == email).first()

    @staticmethod
    def get_demo_by_id(db: Session, _id: int) -> DemoRequest | None:
        return db.query(DemoRequest).filter(DemoRequest.id == _id).first()

    @staticmethod
    def get_demo_list(db: Session) -> DemoRequest | None:
        return db.query(DemoRequest).filter(DemoRequest.deleted_at is not None).all()

    @staticmethod
    def create(db: Session, demo_request: DemoRequest) -> DemoRequest:
        db.add(demo_request)
        db.commit()
        db.refresh(demo_request)
        return demo_request

    @staticmethod
    def update(db: Session, demo_request: DemoRequest) -> DemoRequest:
        demo_request = db.merge(demo_request)
        db.commit()
        db.refresh(demo_request)
        return demo_request
