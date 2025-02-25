from fastapi import APIRouter, Depends, Path, Query

from app import dto, schemas
from app.api.api_v1.deps import authenticate_user, get_project_service_instance
from app.models import Project, User
from app.services.project import ProjectService

router = APIRouter()


@router.get("/test")
async def test(user=Depends(authenticate_user)):
    return user.name


@router.post("/", response_model=dto.Project)
async def create_project(
    project_in: schemas.Project,
    project_service: ProjectService = Depends(get_project_service_instance),
    user: User = Depends(authenticate_user),
):
    project = project_service.create(project_in, user=user)
    return project


@router.get("/{id}", response_model=dto.Project)
async def get_project(
    _id: int = Path(alias="id"),
    project_service: ProjectService = Depends(get_project_service_instance),
    user: User = Depends(authenticate_user),
):
    project = project_service.get(_id, user)
    return project


@router.get("/list/", response_model=list[dto.Project])
async def get_all_projects(
    skip: int = Query(ge=0, default=0),
    limit: int = Query(le=100, default=100),
    project_service: ProjectService = Depends(get_project_service_instance),
    user: User = Depends(authenticate_user),
):
    projects = project_service.get_all(skip, limit, user)
    return projects


@router.delete("/delete/{id}")
async def delete_project(
    _id: int = Path(alias="id"),
    user: User = Depends(authenticate_user),
    project_service: ProjectService = Depends(get_project_service_instance),
) -> dict:
    project: Project = project_service.delete(_id=_id, user=user)
    return {"message": "Project deleted successfully", "project_id": project.id}


# @router.get("/user/list")
# async def get_all_from_user(skip: int = Query(ge=0, default=0), limit: int = Query(le=100, default=100),
#                             project_service: ProjectService = Depends(get_project_service_instance),
#                             user_service: UserService = Depends(get_user_service_instance)):
#     return user_service.get_user().projects


@router.post(path="/filter", response_model=list[dto.Project])
async def filter_project(
    filter_param: schemas.ProjectFilter,
    skip: int = Query(ge=0, default=0),
    limit: int = Query(le=100, default=100),
    user: User = Depends(authenticate_user),
    project_service: ProjectService = Depends(get_project_service_instance),
):
    projects = project_service.filter(skip, limit, user, filter_param)
    return projects
