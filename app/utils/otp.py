import secrets
import string

from app import schemas
from app.utils.mail import MailSchema, send_mail


def generate_otp():
    return "".join(secrets.choice(string.digits) for _ in range(5))


def send_otp_mail(otp: schemas.OTP, subject: str, template: str):
    mail_schema = MailSchema(
        to=otp.email,
        subject=subject,
        from_="No Reply-FEZtool<info@feztool.com>",
        template=template,
        content={"otp_code": otp.code},
    )
    send_mail(mail_schema)
