from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from .config import settings

engine = create_engine(url=settings.sqlalchemy_database_url)

SessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)
session = SessionLocal()

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
