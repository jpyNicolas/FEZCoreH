from sqlalchemy.orm import Session

from app.models import OTP


class OTPCrud:
    @staticmethod
    def get(db: Session, email: str):
        return db.query(OTP).filter(OTP.email == email).first()

    @staticmethod
    def create(db: Session, otp: OTP):
        db.add(otp)
        db.commit()
        db.refresh(otp)
        return otp

    @staticmethod
    def update(db: Session, otp: OTP):
        otp = db.merge(otp)
        db.commit()
        db.refresh(otp)
        return otp

    @staticmethod
    def delete(db: Session, email: str):
        otp = OTPCrud.get(db, email)
        if otp:
            db.delete(otp)
            db.commit()
