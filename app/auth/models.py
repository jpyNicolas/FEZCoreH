from sqlalchemy import Column, String

from app.auth.database import Base


class Token(Base):
    __tablename__ = "tokens"

    sub = Column(String, primary_key=True, index=True)
    token = Column(String)
