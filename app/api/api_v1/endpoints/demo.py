# Import packages, libraries and dependencies
from enum import Enum

from fastapi import APIRouter, Depends, HTTPException, Path, status

from app.api.api_v1.deps import (
    authenticate_user,
    get_demo_request_service_instance,
    get_user_service_instance,
)
from app.dto import DemoRequestInfo, DemoRequestSingle

# Import functionalities
from app.models import User
from app.schemas import NewDemoRequest
from app.services.demo import DemoRequestService
from app.services.user import UserService

# Create instance from APIRouter
router = APIRouter()


# Send request to get demo
@router.post(
    path="/request",
    name="demo request",
    description="Submit a request for a demo of application",
    status_code=status.HTTP_201_CREATED,
    tags="demo",
    response_model=DemoRequestInfo,
)
async def demo_request(
    demo_data: NewDemoRequest,
    demo_request_service: DemoRequestService = Depends(
        get_demo_request_service_instance
    ),
) -> DemoRequestInfo:
    created_demo_request = demo_request_service.create_new_demo_request(demo_data)
    return created_demo_request


# Single request information
@router.get(
    path="/info/{id}",
    name="single demo request",
    description="Get single demo request information",
    status_code=status.HTTP_200_OK,
    tags="demo",
    response_model=DemoRequestSingle,
)
async def demo_information(
    _id: int = Path(alias="id"),
    user: User = Depends(authenticate_user),
    user_service: UserService = Depends(get_user_service_instance),
    demo_request_service: DemoRequestService = Depends(
        get_demo_request_service_instance
    ),
) -> DemoRequestSingle:
    # Check authorization user (is our user has admin role?)
    is_admin = user_service.check_user_admin(user.id)
    if is_admin is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You do not have permission to view requests.",
        )

    single_demo_request = demo_request_service.find_single_demo_request(id=_id)
    return single_demo_request


# Get request list
@router.get(
    path="/list",
    name="demo request list",
    description="Get list of demo requests",
    status_code=status.HTTP_200_OK,
    tags="demo",
    response_model=list[DemoRequestSingle],
)
async def demo_list(
    user: User = Depends(authenticate_user),
    user_service: UserService = Depends(get_user_service_instance),
    demo_request_service: DemoRequestService = Depends(
        get_demo_request_service_instance
    ),
) -> list[DemoRequestSingle]:
    is_admin = user_service.check_user_admin(user.id)
    if is_admin is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You do not have permission to view requests.",
        )

    demo_requests = demo_request_service.find_demo_requests(None)
    return demo_requests


class Vote(Enum):
    approve = "approve"
    reject = "reject"


# Review demo request
@router.put(
    path="/vote/{id}/{vote}",
    name="Vote demo request",
    description="Accept or reject demo requests via admin",
    status_code=status.HTTP_200_OK,
    tags="demo",
    response_model=DemoRequestSingle,
)
async def demo_accept(
    _id: int = Path(alias="id"),
    vote: Vote = Path(alias="vote"),
    user: User = Depends(authenticate_user),
    user_service: UserService = Depends(get_user_service_instance),
    demo_request_service: DemoRequestService = Depends(
        get_demo_request_service_instance
    ),
) -> DemoRequestSingle:
    is_admin = user_service.check_user_admin(user.id)
    if is_admin is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You do not have permission to view requests.",
        )
    checked_demo_request = demo_request_service.review_demo_request(
        status=vote, _id=_id
    )
    return checked_demo_request


# Delete demo request
