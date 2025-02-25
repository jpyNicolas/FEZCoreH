import datetime

from fastapi import BackgroundTasks, HTTPException, status
from sqlalchemy.orm import Session

from app import schemas
from app.api.api_v1.deps import get_user_by_token, validate_user_credentials
from app.auth.jwt_auth import (
    check_refresh_token,
    create_access_token,
    create_refresh_token,
)
from app.crud.demo import DemoRequestCRUD
from app.crud.otp import OTPCrud
from app.crud.rp_otp import RPOTPCrud
from app.crud.user import USERCrud
from app.models import OTP, DemoRequest, ResetPasswordOTP, User
from app.utils.hashing import Hash
from app.utils.otp import generate_otp, send_otp_mail


class AuthService:
    def __init__(self, db: Session, auth_db: Session | None = None):
        self.db = db
        self.auth_db = auth_db

    def signup(
        self, user_in: schemas.UserCreate, key: str, background_task: BackgroundTasks
    ) -> User:
        user = USERCrud.get_by_email(self.db, user_in.email)  # type: ignore
        if user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Email already registered"
            )

        # User approved request
        # key is valid
        # key is not expired
        demo_request: DemoRequest = DemoRequestCRUD.get_demo_signin(
            self.db, email=user_in.email
        )
        if demo_request is None:
            raise HTTPException(
                status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
                detail="The key or email is invalid, please try to get a new link to register.",
            )
        else:
            if demo_request.key != key:
                raise HTTPException(
                    status_code=status.HTTP_406_NOT_ACCEPTABLE,
                    detail="The parameter key sent is invalid. Please try again to get a new URL.",
                )
            print("------------------------------------------------------------")
            print(demo_request.expired_key)
            print(datetime.datetime.now())
            print("------------------------------------------------------------")
            if demo_request.expired_key < datetime.datetime.now():
                raise HTTPException(
                    status_code=status.HTTP_428_PRECONDITION_REQUIRED,
                    detail="The specified date for creating an account has expired, please try again to get the demo.",
                )

        user_model = User(
            email=user_in.email,
            hashed_password=Hash.bcrypt(user_in.password),
            name=user_in.name,
        )

        user = USERCrud.create(self.db, user_model)

        otp_model = OTP(email=user_model.email, code=generate_otp())
        otp = OTPCrud.create(self.db, otp_model)

        otp_mail_schema = schemas.OTP(
            email=otp.email,
            code=otp.code,
        )

        background_task.add_task(
            func=send_otp_mail,
            otp=otp_mail_schema,
            subject="Account Verification",
            template="account_verification.html",
        )
        return user

    def get_tokens(self, signin_data: schemas.SignInUser) -> dict:
        user: User = USERCrud.get_by_email(self.db, signin_data.email)
        print("kos")
        print("kir")
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if not Hash.verify_password(signin_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        try:
            validate_user_credentials(user)
        except HTTPException as e:
            raise e
        access_token = create_access_token(
            data={"sub": user.email, "id": user.id, "role": user.role.name}
        )
        refresh_token = create_refresh_token(data={"sub": user.email}, db=self.auth_db)
        return {
            "token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    def get_access_from_refresh_token(self, refresh_token: str) -> dict:
        if not check_refresh_token(db=self.auth_db, refresh_token=refresh_token):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        user = get_user_by_token(self.db, refresh_token)
        access_token = create_access_token(
            data={"sub": user.email, "id": user.id, "role": user.role.name}
        )
        return {"token": access_token, "token_type": "bearer"}

    def confirm_account(self, email: str, code: str) -> None:
        otp = OTPCrud.get(self.db, email)

        if not otp:
            user = USERCrud.get_by_email(self.db, email)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
                )
            elif user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Account already confirmed",
                )

        if otp.code != code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid confirmation code",
            )

        if (
            datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
            - otp.updated_at
        ) >= datetime.timedelta(minutes=5):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Account confirmation code has expired",
            )

        user = USERCrud.get_by_email(self.db, email)
        user.is_active = True
        USERCrud.update(self.db, user)
        print(user)
        OTPCrud.delete(self.db, email)

    def resend_confirmation_code_mail(
        self, email: str, background_task: BackgroundTasks
    ) -> None:
        otp = OTPCrud.get(self.db, email)

        if not otp:
            user = USERCrud.get_by_email(self.db, email)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Account not found"
                )
            if user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Account was confirmed",
                )

        if (
            datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
            - otp.updated_at
        ) >= datetime.timedelta(minutes=5):
            otp.code = generate_otp()

        otp = OTPCrud.update(self.db, otp)

        otp_mail_schema = schemas.OTP(
            email=otp.email,
            code=otp.code,
        )
        background_task.add_task(
            func=send_otp_mail,
            otp=otp_mail_schema,
            subject="Account Verification",
            template="account_verification.html",
        )

    def send_recovery_password_mail(
        self, email: str, background_task: BackgroundTasks
    ) -> None:
        otp = RPOTPCrud.get(self.db, email)

        if otp:
            if (
                datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
                - otp.updated_at
            ) >= datetime.timedelta(minutes=5):
                otp.code = generate_otp()

            otp.updated_at = datetime.datetime.now(datetime.timezone.utc)
            otp = RPOTPCrud.update(self.db, otp)
        else:
            otp_model = ResetPasswordOTP(email=email, code=generate_otp())
            otp = RPOTPCrud.create(self.db, otp_model)

        otp_schema = schemas.OTP(email=otp.email, code=otp.code)
        background_task.add_task(
            func=send_otp_mail,
            otp=otp_schema,
            subject="Reset password",
            template="reset_password.html",
        )

    def recovery_password(self, account_in: schemas.RecoveryPassword) -> None:
        otp = RPOTPCrud.get(self.db, account_in.email)
        if not otp:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Not found"
            )
        if account_in.code != otp.code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect reset password code",
            )
        if (
            datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
            - otp.updated_at
        ) >= datetime.timedelta(minutes=5):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Reset password code has expired",
            )

        user = USERCrud.get_by_email(self.db, otp.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        user.hashed_password = Hash.bcrypt(account_in.password)
        USERCrud.update(self.db, user)
        RPOTPCrud.delete(self.db, otp.email)

    def check_reset_password_otp(self, email, code):
        otp_db: OTP = RPOTPCrud.get(self.db, email)
        if not otp_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="OTP not found"
            )
        if not otp_db.code == code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Wrong code"
            )
        return
