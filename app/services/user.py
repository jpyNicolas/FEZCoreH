from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app import schemas
from app.crud.user import USERCrud
from app.models import Admin, User
from app.services.apikey import ApiKeyService
from app.utils.hashing import Hash


class UserService:
    def __init__(self, db: Session, user: User):
        self.db = db
        self.user = user

    def get_user(self):
        return self.user

    def change_password(self, password_data: schemas.ChangePassword):
        if not Hash.verify_password(password_data.password, self.user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect password"
            )
        self.user.hashed_password = Hash.bcrypt(password_data.new_password)
        USERCrud.update(self.db, self.user)

    def generate_key(self, name: str):
        if len(self.user.api_keys) >= 5:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User cannot have more than 5 API keys.",
            )

        apikey_service = ApiKeyService(db=self.db)
        try:
            apikey = apikey_service.create(name, user_id=self.user.id)
        except HTTPException as e:
            raise e
        return apikey

    def has_apikey(self):
        if not self.user.api_keys:
            return False
        return True

    def delete_api_key(self, _id: int):
        apikey_service = ApiKeyService(db=self.db)

    def check_user_admin(self, _id: int) -> Admin:
        return USERCrud.get_admin_by_id(self.db, id=_id)
