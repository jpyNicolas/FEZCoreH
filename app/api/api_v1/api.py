from fastapi import APIRouter

from app.api.api_v1.endpoints import (
    apikey,
    auth,
    contact,
    demo,
    file,
    operation,
    project,
    user,
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(user.router, prefix="/user", tags=["user"])
api_router.include_router(apikey.router, prefix="/apikey", tags=["apikey"])
api_router.include_router(project.router, prefix="/project", tags=["project"])
api_router.include_router(file.router, prefix="/file", tags=["file"])
api_router.include_router(operation.router, prefix="/operation", tags=["operation"])
api_router.include_router(contact.router, prefix="/contact", tags=["contact"])
api_router.include_router(demo.router, prefix="/demo", tags=["demo"])
