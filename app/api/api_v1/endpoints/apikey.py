from fastapi import APIRouter, Depends, Path
from starlette import status

from app import dto
from app.api.api_v1.deps import get_user_service_instance, authenticate_user, \
    get_apikey_service_instance
from app.models import User
from app.services.apikey import ApiKeyService
from app.services.user import UserService

router = APIRouter()


@router.post("/generate-apikey", response_model=dto.ApiKey)
async def generate_apikey(name: str, user_service: UserService = Depends(get_user_service_instance)):
    return user_service.generate_key(name)


@router.get("/", response_model=dto.ShowApiKey)
async def get_apikey_detail(_id: int = Path(alias="id"),
                            user: User = Depends(authenticate_user, use_cache=False),
                            apikey_service: ApiKeyService = Depends(get_apikey_service_instance)):
    return apikey_service.get(_id, user)


@router.delete("/{id}", status_code=status.HTTP_200_OK)
async def delete_api_key(_id: int = Path(alias="id"),
                         user: User = Depends(authenticate_user, use_cache=False),
                         apikey_service: ApiKeyService = Depends(get_apikey_service_instance)):
    return apikey_service.delete(_id, user)
