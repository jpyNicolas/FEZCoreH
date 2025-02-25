from datetime import datetime, timedelta
from enum import Enum

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.crud.demo import DemoRequestCRUD
from app.models import DemoRequest
from app.schemas import NewDemoRequest
from app.utils.mail import MailSchema, send_mail
from app.utils.otp import generate_otp


class DemoRequestService:
    def __init__(self, db: Session, demo_db: Session | None = None):
        self.db = db
        self.demo_db = demo_db

    def create_new_demo_request(self, demo_data: NewDemoRequest) -> DemoRequest:
        get_demo_by_email = DemoRequestCRUD.get_demo_by_email(
            db=self.db, email=demo_data.email
        )
        if get_demo_by_email is None:
            try:
                demo_data = DemoRequest(
                    email=demo_data.email,
                    company_name=demo_data.company_name,
                    message=demo_data.message,
                )
                create_demo_request = DemoRequestCRUD.create(
                    db=self.db, demo_request=demo_data
                )

                # Send email to requester
                # I should refactor this line code, and split these line from main body
                # This task must run in background
                send_acknowledge_email = MailSchema(
                    to=create_demo_request.email,
                    subject="Your demo request has been sent",
                    from_="No Reply-FEZtool<info@feztool.com>",
                    template="demo_request_submitted.html",
                    content={
                        "email": create_demo_request.email,
                        "company_name": create_demo_request.company_name,
                    },
                )
                send_mail(send_acknowledge_email)

                return create_demo_request
            except Exception as exception:
                print(exception)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="An error occurred while the application was trying to process your request. Please contact support and try again later.",
                )
        elif get_demo_by_email.approved is None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"A request has already been made to receive a demo with email address {demo_data.email}.",
            )
        else:
            if get_demo_by_email.approved is True:
                raise HTTPException(
                    status_code=status.HTTP_308_PERMANENT_REDIRECT,
                    detail=f"Your request has been approved with email {demo_data.email} and you will be taken to the singin page.",
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_406_NOT_ACCEPTABLE,
                    detail=f"A previous request to this email {demo_data.email} has been rejected, please email Feztool Support.",
                )

    def find_single_demo_request(self, id: int) -> DemoRequest:
        get_demo_request_by_id = DemoRequestCRUD.get_demo_by_id(db=self.db, _id=id)
        if get_demo_request_by_id is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No request with ID {id} found.",
            )

        return get_demo_request_by_id

    def find_demo_requests(self, filter: dict | None) -> DemoRequest | None:
        get_demo_requests = DemoRequestCRUD.get_demo_list(db=self.db)
        return get_demo_requests

    class Vote(Enum):
        approve = "approve"
        reject = "reject"

    def review_demo_request(self, _id: int, status: Vote) -> DemoRequest:
        print(status)
        if status.value == "reject":
            status = False
        else:
            status = True

        until_expiration = datetime.now() + timedelta(weeks=2)

        demo_request = self.find_single_demo_request(id=_id)
        demo_request.approved = status
        demo_request.key = generate_otp()
        demo_request.expired_key = until_expiration

        # Update status
        checked_demo_request = DemoRequestCRUD.update(
            self.db, demo_request=demo_request
        )

        # Send email to request mail
        # These block codes should refactor later
        try:
            mail_schema = MailSchema(
                to=checked_demo_request.email,
                subject="Thank You for Reaching Out",
                from_="No Reply-FEZtool<info@feztool.com>",
                template="review_demo_request.html",
                content={
                    "email": checked_demo_request.email,
                    "company_name": checked_demo_request.company_name,
                    "approved": demo_request.approved,
                    "url": f"https://app.feztool.com/auth/signup/?key={checked_demo_request.key}",
                    "expired_in": until_expiration,
                },
            )
            send_mail(mail_schema)
        except Exception as exception:
            print(exception)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while the application was trying to send email to client.",
            )
        return checked_demo_request
