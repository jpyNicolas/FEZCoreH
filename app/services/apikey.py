import secrets

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.crud.apikey import ApiKeyCrud
from app.models import ApiKey, User


class ApiKeyService:
    def __init__(self, db: Session):
        self.db = db

    def create(self, name: str, user: User):
        if ApiKeyCrud.get_by_name(self.db, user, name):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail="Duplicate apikey name")

        key = secrets.token_urlsafe(64)
        new_apikey = ApiKey(
            key=key,
            name=name,
            user=user
        )
        apikey = ApiKeyCrud.create(db=self.db, apikey=new_apikey)
        return apikey

    def get(self, _id: int, user: User) -> ApiKey:
        apikey = ApiKeyCrud.get(self.db, user, _id)
        if not apikey:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Apikey not found"
            )
        return apikey

    def authenticate_apikey(self, key: str):
        apikey = ApiKeyCrud.get_by_key(self.db, key)
        if not apikey:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Apikey not found")
        return apikey

    def delete(self, _id: int, user: User) -> bool:
        check = ApiKeyCrud.delete(self.db, user, _id)
        if not check:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
