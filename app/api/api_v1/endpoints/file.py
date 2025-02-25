from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Path,
    UploadFile,
    status,
)

from app import dto
from app.api.api_v1.deps import get_file_service_instance, retrieve_project
from app.config import settings
from app.models import Project
from app.services.file import FileService

router = APIRouter()

ALLOWED_FILE_EXTENSION = ["tiff", "tif"]


@router.post("/upload", response_model=dto.File)
async def upload_file(
    filename: str | None = Form(None),
    file: UploadFile = File(...),
    file_service: FileService = Depends(get_file_service_instance),
    project: Project = Depends(retrieve_project),
):
    try:
        filename_parts = file.filename.rsplit(".", 1)

        extension = filename_parts[1]
        filename = filename_parts[0] if not filename else filename
        if extension not in ALLOWED_FILE_EXTENSION:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid file extension"
            )
    except IndexError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File should have an extension",
        )

    if file.size > settings.max_size_file:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Size of this file more than {settings.max_size_file}",
        )

    file_model = file_service.create(file, filename, extension, project)
    return file_model


@router.delete(
    "/delete/{id}", response_model=dict, status_code=status.HTTP_202_ACCEPTED
)
async def soft_delete_file(
    file_id: int = Path(alias="id"),
    file_service: FileService = Depends(get_file_service_instance),
) -> dict:
    delete_file_result = file_service.soft_delete(_id=file_id)
    if delete_file_result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File may deleted before or never saved by this ID {file_id}",
        )

    return {"message": "File deleted successfully"}
