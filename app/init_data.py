import logging

from sqlalchemy.orm import Session

from app.config import settings
from app.crud.saved_location import SavedLocationCrud
from app.databese import engine
from app.models import SavedLocation, SavedLocationType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_saved_location(db: Session):
    location_model = (db.query(SavedLocation).
                      filter(SavedLocation.location == settings.OBJECT_STORAGE_URL).first())
    if not location_model:
        location_in = SavedLocation(
            location=settings.OBJECT_STORAGE_URL,
            type=SavedLocationType.external,
            is_active=True,
            endpoint=settings.OBJECT_STORAGE_ENDPOINT,
            access_key=settings.OBJECT_STORAGE_ACCESS_KEY,
            secret_key=settings.OBJECT_STORAGE_SECRET_KEY,
            bucket_name=settings.OBJECT_STORAGE_BUCKET_NAME
        )
        location_model = SavedLocationCrud.create(db, location_in)
    SavedLocationCrud.activate_location(db, location_model.id)


def init():
    logger.info("Create initial saved location data")
    init_saved_location(Session(bind=engine, autoflush=False, autocommit=False))
    logger.info("Initial saved location data created")


if __name__ == "__main__":
    init()
