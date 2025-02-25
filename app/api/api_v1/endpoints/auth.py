from fastapi import APIRouter, BackgroundTasks, Depends, status
from sqlalchemy.orm import Session

import app.dto
from app import schemas
from app.api.api_v1.deps import validate_user_by_email
from app.auth.database import get_db as get_auth_db
from app.databese import get_db
from app.schemas import EmailStr
from app.services.auth import AuthService

router = APIRouter()


def get_auth_service(
    db: Session = Depends(get_db), _auth_db: Session = Depends(get_auth_db)
):
    return AuthService(db, _auth_db)


@router.post(
    "/signup", response_model=app.dto.ShowUser, status_code=status.HTTP_201_CREATED
)
async def signup(
    key: str,
    request: schemas.UserCreate,
    background_task: BackgroundTasks,
    auth_service: AuthService = Depends(get_auth_service),
):
    user = auth_service.signup(request, key, background_task)
    return user


@router.post("/token", status_code=status.HTTP_200_OK)
async def login_for_access_token(
    request: schemas.SignInUser, auth_service: AuthService = Depends(get_auth_service)
):
    tokens = auth_service.get_tokens(request)
    return tokens


@router.get("/refresh", status_code=status.HTTP_200_OK)
async def get_access_token_from_refresh_token(
    refresh_token: str, auth_service: AuthService = Depends(get_auth_service)
):
    token = auth_service.get_access_from_refresh_token(refresh_token)
    return token


@router.post("/confirm", status_code=status.HTTP_204_NO_CONTENT)
async def confirm_account(
    request: schemas.Confirm, auth_service: AuthService = Depends(get_auth_service)
):
    auth_service.confirm_account(request.email, request.code)


@router.post("/resend-confirmation", status_code=status.HTTP_204_NO_CONTENT)
async def resend_confirmation(
    background_task: BackgroundTasks,
    email: EmailStr,
    auth_service: AuthService = Depends(get_auth_service),
):
    auth_service.resend_confirmation_code_mail(email, background_task)


@router.get(
    "/send-reset-password-code",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(validate_user_by_email)],
)
async def send_recovery_password_mail(
    background_task: BackgroundTasks,
    email: EmailStr,
    auth_service: AuthService = Depends(get_auth_service),
):
    auth_service.send_recovery_password_mail(email, background_task)


@router.post("/reset-password", status_code=status.HTTP_204_NO_CONTENT)
async def recovery_password(
    account_in: schemas.RecoveryPassword,
    auth_service: AuthService = Depends(get_auth_service),
):
    auth_service.recovery_password(account_in)


@router.post("/check-otp")
async def check_otp(
    request: schemas.OTP, auth_service: AuthService = Depends(get_auth_service)
):
    auth_service.check_reset_password_otp(request.email, request.code)


@router.get("/logout")
async def logout():
    return
