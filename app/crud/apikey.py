from sqlalchemy.orm import Session

from app.models import ApiKey, User


class ApiKeyCrud:
    @staticmethod
    def create(db: Session, apikey: ApiKey) -> ApiKey:
        db.add(apikey)
        db.commit()
        db.refresh(apikey)
        return apikey

    @staticmethod
    def get(db: Session, user: User, _id: int) -> ApiKey:
        return db.query(ApiKey).filter(ApiKey.id == _id).filter(ApiKey.user == user).first()

    @staticmethod
    def get_by_key(db: Session, key: str) -> ApiKey:
        return db.query(ApiKey).filter(ApiKey.key == key).first()

    @staticmethod
    def get_by_name(db: Session, user: User, name: str) -> ApiKey | None:
        return (db.query(ApiKey)
                .filter(ApiKey.user == user)
                .filter(ApiKey.name == name).first())

    @staticmethod
    def update(db: Session, apikey: ApiKey) -> ApiKey:
        apikey = db.merge(apikey)
        db.commit()
        db.refresh(apikey)
        return apikey

    @staticmethod
    def delete(db: Session, user: User, _id: int) -> bool:
        apikey = ApiKeyCrud.get(db, user, _id)
        if apikey:
            db.delete(apikey)
            db.commit()
            return True
        return False
