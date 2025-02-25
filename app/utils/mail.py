import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from pydantic import BaseModel

from app.config import settings


class MailSchema(BaseModel):
    subject: str
    from_: str
    to: str
    template: str | None = None
    content: dict | None = None
    plain_text_message: str | None = None


def send_mail(mail: MailSchema):
    message = MIMEMultipart()
    message["Subject"] = mail.subject
    message["From"] = mail.from_
    message["To"] = mail.to
    template = Environment(loader=FileSystemLoader(Path(__file__).parent.parent / "templates")).get_template(
        mail.template) \
        if mail.template else None

    if template:
        if mail.content:
            message.attach(MIMEText(template.render(**mail.content), "html"))
        else:
            message.attach(MIMEText(template.render(), "html"))

    if mail.plain_text_message:
        message.attach(MIMEText(mail.plain_text_message, "plain"))

    with smtplib.SMTP(settings.smtp_server, settings.smtp_port) as server:
        server.ehlo()
        server.starttls()
        server.login(settings.smtp_user, settings.smtp_password)
        server.sendmail(
            settings.mail_from, mail.to, message.as_string()
        )
