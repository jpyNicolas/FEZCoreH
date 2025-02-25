from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from jose import JWTError, jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.auth import models
from app.auth.config import settings


def check_secret_key():
    if not settings.secret_key:
        raise Exception("You must declare secret-key")


check_secret_key()

bearer_scheme = HTTPBearer()


def get_token(token=Depends(bearer_scheme)) -> str:
    return str(token.credentials)


def get_token_data(token: str = Depends(get_token)) -> dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        data = jwt.decode(
            token=token, key=settings.secret_key, algorithms=[settings.jwt_algorithm]
        )
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return data


def create_jwt_token(data: dict, expire: timedelta) -> str:
    payload = data.copy()
    utc = timezone.utc
    exp = datetime.now(utc) + expire
    payload.update({"exp": exp})
    encoded = jwt.encode(
        payload, key=settings.secret_key, algorithm=settings.jwt_algorithm
    )
    return encoded


def create_access_token(data: dict) -> str:
    return create_jwt_token(
        data, expire=timedelta(days=settings.access_token_expire_days)
    )


def create_refresh_token(data: dict, db: Session) -> str:
    token = create_jwt_token(
        data, expire=timedelta(days=settings.refresh_token_expire_days)
    )
    existing_token = (
        db.query(models.Token).filter(models.Token.sub == data.get("sub")).first()
    )
    if existing_token:
        existing_token.token = token
    else:
        instance = models.Token(sub=data.get("sub"), token=token)
        db.add(instance)
    db.commit()
    return token


def check_refresh_token(db: Session, refresh_token: str) -> bool:
    token = db.query(models.Token).filter(models.Token.token == refresh_token).first()
    if not token:
        return False
    return True
