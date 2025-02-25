from sqlalchemy.orm import Session

from app.models import SavedLocation


class SavedLocationCrud:

    @staticmethod
    def create(db: Session, saved_location: SavedLocation) -> SavedLocation:
        db.add(saved_location)
        db.commit()
        db.refresh(saved_location)
        return saved_location

    @staticmethod
    def get(db: Session, _id: int) -> SavedLocation | None:
        return db.query(SavedLocation).filter(SavedLocation.id == _id).first()

    @staticmethod
    def get_active(db: Session) -> SavedLocation | None:
        return (db.query(SavedLocation)
                .filter(SavedLocation.is_active).first())

    @staticmethod
    def activate_location(db: Session, _id: int) -> None:
        db.query(SavedLocation).update({SavedLocation.is_active: False})
        (db.query(SavedLocation).
         filter(SavedLocation.id == _id).
         update({SavedLocation.is_active: True}))
        db.commit()

    @staticmethod
    def update(db: Session, saved_location: SavedLocation) -> SavedLocation:
        saved_location = db.merge(saved_location)
        db.commit()
        db.refresh(saved_location)
        return saved_location
