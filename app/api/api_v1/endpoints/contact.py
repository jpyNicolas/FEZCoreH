from fastapi import APIRouter, BackgroundTasks, status

from app import schemas
from app.utils.mail import MailSchema, send_mail

router = APIRouter()


@router.post(
    name="Contact Us",
    path="",
    status_code=status.HTTP_200_OK,
    tags=["contact"],
    description="This is the endpoint for sending mail to feztool (team).",
)
async def contact_us(
    contact_form_info: schemas.ContactUsForm, background_task: BackgroundTasks
) -> str:

    # Send email to info@feztool.com
    mail_schema = MailSchema(
        to="info@feztool.com",
        subject="Contact",
        from_="No Reply-Client<info@feztool.com>",
        template="contact_us.html",
        content={
            "message": contact_form_info.message,
            "email": contact_form_info.email,
        },
    )
    send_mail(mail_schema)

    # Ack to email
    mail_schema = MailSchema(
        to=contact_form_info.email,
        subject="Thank You for Reaching Out",
        from_="No Reply-FEZtool<info@feztool.com>",
        template="confirm_contact_us.html",
        content={"email": contact_form_info.email},
    )
    send_mail(mail_schema)

    return "Email sent successfully."
