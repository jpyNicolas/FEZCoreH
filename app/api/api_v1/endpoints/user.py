from fastapi import APIRouter, Depends, status

from app import schemas, dto
from app.api.api_v1.deps import get_user_service_instance
from app.services.user import UserService

router = APIRouter()


@router.get("/", response_model=dto.ShowUser)
async def get_user(user_service: UserService = Depends(get_user_service_instance)):
    return user_service.get_user()


@router.put("/change-password", status_code=status.HTTP_202_ACCEPTED)
async def change_password(password_data: schemas.ChangePassword,
                          user_service: UserService = Depends(get_user_service_instance)):
    user_service.change_password(password_data)


@router.get("/has_apikey")
async def has_apikey(user_service: UserService = Depends(get_user_service_instance)):
    return user_service.has_apikey()
