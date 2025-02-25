from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query, status

from app import dto
from app.api.api_v1.deps import (
    authenticate_user,
    get_operation_service_instance,
    get_project_service_instance,
    retrieve_project,
)
from app.models import OperationOutput, Project
from app.schemas import Bands
from app.services.operation import Operation
from app.services.project import ProjectService

router = APIRouter()


@router.post("/", response_model=dto.OperationOutput)
async def operation(
    bands: Bands,
    tif_file: int | None = Body(default=None),
    project: Project = Depends(retrieve_project),
    operation_service: Operation = Depends(get_operation_service_instance),
    operation_type: str = Query(),
    title: str = Query(max_length=50),
    extra_params: dict | None = None,
    project_service: ProjectService = Depends(get_project_service_instance),
    user=Depends(authenticate_user),
) -> OperationOutput:

    file_model = operation_service.operate(
        tif_file=tif_file,
        bands=bands,
        operation_type=operation_type,
        title=title,
        project=project,
        extra_params=extra_params,
    )

    # Update modified_at time project
    project_service.change_updated_at_time(
        _id=project.id, user=user, last_action=operation_type
    )

    return file_model


@router.delete("/delete/{id}", response_model=dict)
async def delete_operation_output(
    _id: int = Path(alias="id"),
    operation_service: Operation = Depends(get_operation_service_instance),
) -> dict:
    operation_output = operation_service.delete_operation_output(_id=_id)

    if operation_service is None:
        raise HTTPException(
            detail="Something wrong about operation deleting",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    return {
        "message": "Operation deleted successfully",
        "operation_id": operation_output.id,
    }
