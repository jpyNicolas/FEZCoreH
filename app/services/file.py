import os.path
import uuid
from pathlib import Path
from typing import BinaryIO

import boto3
from botocore.exceptions import BotoCoreError, NoCredentialsError
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.config import settings
from app.crud.file import FileCrud
from app.crud.operation import OperationCrud
from app.crud.saved_location import SavedLocationCrud
from app.models import File, OperationOutput, Project
from app.utils import convertor


def _save_file(file_path: Path, file_content: BinaryIO):
    file_content.seek(0)
    with open(file_path, "wb") as f:
        f.write(file_content.read())
    file_content.seek(0)


def _upload_to_s3(location, file: BinaryIO, unique_name: str, extension: str):
    try:
        s3 = boto3.client(
            "s3",
            endpoint_url=location.endpoint,
            aws_access_key_id=location.access_key,
            aws_secret_access_key=location.secret_key,
        )
        s3.upload_fileobj(file, location.bucket_name, f"{unique_name}.{extension}")
    except NoCredentialsError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload file due to missing credentials",
        )
    except BotoCoreError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading file: {str(e)}",
        )


class FileService:
    def __init__(self, db: Session):
        self.db = db

    def create(self, file, filename, extension, project: Project):

        # IDK why Hooman add this to create file method but, I just comment it ...
        # if FileCrud.get_by_name(self.db, filename, project=project):
        #     raise HTTPException(
        #         status_code=status.HTTP_409_CONFLICT,
        #         detail=f"Duplicate filename {filename}",
        #     )

        location = SavedLocationCrud.get_active(self.db)

        unique_name = str(uuid.uuid4())

        folder_path = Path(settings.local_save_files) / "images"
        folder_thumbnail = folder_path / "thumbnails"

        file_path = folder_path / f"{unique_name}.{extension}"

        folder_path.mkdir(parents=True, exist_ok=True)
        folder_thumbnail.mkdir(parents=True, exist_ok=True)

        _save_file(file_path, file.file)

        image_path = folder_path / f"{unique_name}.png"
        convertor.convert_to_png(file_path, image_path, (1080, 1080))
        thumbnail_file_path = folder_thumbnail / f"{unique_name}.png"
        convertor.convert_to_png(file_path, thumbnail_file_path)

        try:
            _upload_to_s3(location, file.file, unique_name, extension)
        finally:
            file_path.unlink(missing_ok=True)

        file_model = File(
            filename=filename,
            unique_name=unique_name,
            extension=extension,
            project=project,
            location=location,
        )
        file_model = FileCrud.create(self.db, file_model)

        return file_model

    def create_operation_output(
        self,
        file_path: Path,
        unique_name: str,
        extension: str,
        project: Project,
        title=str,
    ) -> OperationOutput:
        location = SavedLocationCrud.get_active(self.db)

        with open(file_path, "r+b") as f:
            _upload_to_s3(location, f, unique_name, extension)

        # if file := OperationCrud.get_by_project(self.db, project):
        #     file.unique_name = unique_name
        #     file.extension = extension
        #     file.location = location
        #     return OperationCrud.update(self.db, file)

        output_model = OperationOutput(
            title=title,
            unique_name=unique_name,
            extension=extension,
            project=project,
            location=location,
        )
        output_model = OperationCrud.create(self.db, output_model)
        return output_model

    def get(self, _id: int, project: Project) -> str:
        file = FileCrud.get(self.db, _id, project)
        if not file:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="File not found"
            )

        full_filename = f"{file.unique_name}.{file.extension}"
        location = file.location
        local_file_path = os.path.join(settings.local_save_files, full_filename)

        if not os.path.exists(local_file_path):

            try:
                s3 = boto3.client(
                    "s3",
                    endpoint_url=location.endpoint,
                    aws_access_key_id=location.access_key,
                    aws_secret_access_key=location.secret_key,
                )
                s3.download_file(
                    file.location.bucket_name, full_filename, local_file_path
                )
            except NoCredentialsError:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Missing credentials for downloading the file",
                )
        return local_file_path

    def soft_delete(self, _id: int):
        file = FileCrud.get_by_id(self.db, _id)
        if not file:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="File not found"
            )
        file = FileCrud.soft_delete(self.db, _id=_id)
        return file
