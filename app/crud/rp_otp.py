from sqlalchemy.orm import Session

from app.models import ResetPasswordOTP


class RPOTPCrud:
    @staticmethod
    def get(db: Session, email: str):
        return db.query(ResetPasswordOTP).filter(ResetPasswordOTP.email == email).first()

    @staticmethod
    def create(db: Session, otp: ResetPasswordOTP) -> ResetPasswordOTP:
        db.add(otp)
        db.commit()
        db.refresh(otp)
        return otp

    @staticmethod
    def update(db: Session, otp: ResetPasswordOTP):
        otp = db.merge(otp)
        db.commit()
        db.refresh(otp)
        return otp

    @staticmethod
    def delete(db: Session, email: str):
        otp = RPOTPCrud.get(db, email)
        if otp:
            db.delete(otp)
            db.commit()
