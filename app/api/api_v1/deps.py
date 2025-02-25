from fastapi import Depends, HTTPException, Query, Request, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.auth.jwt_auth import get_token_data
from app.crud.user import USERCrud
from app.databese import get_db
from app.models import Project, User
from app.schemas import EmailStr
from app.services.apikey import ApiKeyService
from app.services.demo import DemoRequestService
from app.services.file import FileService
from app.services.operation import Operation
from app.services.project import ProjectService
from app.services.user import UserService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token", scheme_name="JWT")


def validate_user_credentials(user: User) -> None:
    if user.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Account not confirmed"
        )
    if user.is_banned:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Account has been banned"
        )


def get_user_by_token(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
):
    data = get_token_data(token)
    user = USERCrud.get_by_email(db, data.get("sub"))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def get_valid_user(user: User = Depends(get_user_by_token)):
    validate_user_credentials(user)
    return user


async def authenticate_user(
    request: Request, apikey: str | None = None, db: Session = Depends(get_db)
) -> User:
    if request.headers.get("Authorization"):
        token = await oauth2_scheme(request)
        return get_valid_user(get_user_by_token(db, token))
    elif apikey:
        apikey_service = get_apikey_service_instance(db)
        return retrieve_apikey(key=apikey, apikey_service=apikey_service).user
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
    )


def validate_user_by_email(email: EmailStr, db: Session = Depends(get_db)):
    user = USERCrud.get_by_email(db, email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    try:
        validate_user_credentials(user)
    except HTTPException as e:
        raise e


def get_apikey_service_instance(db: Session = Depends(get_db)):
    return ApiKeyService(db)


def retrieve_apikey(
    key: str, apikey_service: ApiKeyService = Depends(get_apikey_service_instance)
):

    apikey = apikey_service.authenticate_apikey(key)
    return apikey


def get_project_service_instance(db: Session = Depends(get_db)):
    return ProjectService(db)


def retrieve_project(
    project_id: int = Query(),
    project_service: ProjectService = Depends(get_project_service_instance),
    user: User = Depends(authenticate_user),
) -> Project:
    project = project_service.get(project_id, user)
    return project


def get_file_service_instance(db: Session = Depends(get_db)):
    return FileService(db)


def get_user_service_instance(
    db: Session = Depends(get_db),
    user: User = Depends(authenticate_user, use_cache=False),
) -> UserService:
    return UserService(db, user)


def get_operation_service_instance(db: Session = Depends(get_db)):
    return Operation(db)


def get_demo_request_service_instance(db: Session = Depends(get_db)):
    return DemoRequestService(db=db)
