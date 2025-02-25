from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app import schemas
from app.crud.project import ProjectCrud
from app.models import File, OperationOutput, Project, User


class ProjectService:
    def __init__(self, db: Session):
        self.db = db

    def create(self, project_in: schemas.Project, user: User):

        # This exactly like file name ...
        # if ProjectCrud.get_by_name(self.db, project_in.name, user):
        #     raise HTTPException(
        #         status_code=status.HTTP_409_CONFLICT, detail="Duplicate project"
        #     )

        project = Project(
            name=project_in.name, description=project_in.description, user=user
        )
        return ProjectCrud.create(self.db, project)

    def get(self, _id: int, user: User):
        project = ProjectCrud.get(self.db, _id=_id, user=user)
        if not project or project.deleted_at is not None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
            )

        if project.files is None:
            pass
        else:

            def filter_deleted_files(file: File):
                if file.deleted_at is None:
                    return True
                else:
                    return False

            new_project_files = list(filter(filter_deleted_files, project.files))

        # Filter deleted operation outputs from projects
        if project.operation_output is None:
            pass
        else:

            def filter_deleted_operation(operation_output: OperationOutput):
                if operation_output.deleted_at is None:
                    return True
                else:
                    return False

            new_project_operation_output = list(
                filter(filter_deleted_operation, project.operation_output)
            )

        # prepare project information
        project.files.clear()
        project.files.extend(new_project_files)

        project.operation_output.clear()
        project.operation_output.extend(new_project_operation_output)

        return project

    def get_all(self, skip: int, limit: int, user: User):
        projects: list[Project] = ProjectCrud.get_all(self.db, user, skip, limit)

        if not projects:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You don't have a project",
            )

        # Remove deleted files and operation outputs from project response
        new_project_files = None
        new_project_operation_output = None
        for project in projects:

            # Filter deleted files from projects
            if project.files is None:
                continue
            else:

                def filter_deleted_files(file: File):
                    if file.deleted_at is None:
                        return True
                    else:
                        return False

                new_project_files = list(filter(filter_deleted_files, project.files))

            # Filter deleted operation outputs from projects
            if project.operation_output is None:
                continue
            else:

                def filter_deleted_operation(operation_output: OperationOutput):
                    if operation_output.deleted_at is None:
                        return True
                    else:
                        return False

                new_project_operation_output = list(
                    filter(filter_deleted_operation, project.operation_output)
                )

            # prepare project information
            project.files.clear()
            project.files.extend(new_project_files)

            project.operation_output.clear()
            project.operation_output.extend(new_project_operation_output)

        return projects

    def delete(self, _id: int, user: User) -> Project:
        project = self.get(_id=_id, user=user)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
            )
        project.deleted_at = datetime.now()

        for project_file in project.files:
            project_file.project_id = project.id
            project_file.deleted_at = datetime.now()

        for project_operation in project.operation_output:
            project_operation.project_id = project.id
            project_operation.deleted_at = datetime.now()

        project = ProjectCrud.update(db=self.db, project=project)

        return project

    def change_updated_at_time(self, _id: int, user: User, last_action: str) -> Project:
        project = self.get(_id=_id, user=user)
        project.updated_at = datetime.now()
        project.last_action = last_action
        project = ProjectCrud.update(db=self.db, project=project)
        return project

    def filter(
        self,
        skip: int,
        limit: int,
        user: User,
        parameters: schemas.ProjectFilter | None = None,
    ):
        name = (
            parameters.name if parameters.name and type(parameters.name) is str else ""
        )
        description = (
            parameters.description
            if parameters.description and type(parameters.description) is str
            else ""
        )
        projects: list[Project] = ProjectCrud.get_filter(
            self.db,
            user,
            skip,
            limit,
            name,
            description,
        )

        if not projects:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You don't have a project",
            )

        # Remove deleted files and operation outputs from project response
        new_project_files = None
        new_project_operation_output = None
        for project in projects:

            # Filter deleted files from projects
            if project.files is None:
                continue
            else:

                def filter_deleted_files(file: File):
                    if file.deleted_at is None:
                        return True
                    else:
                        return False

                new_project_files = list(filter(filter_deleted_files, project.files))

            # Filter deleted operation outputs from projects
            if project.operation_output is None:
                continue
            else:

                def filter_deleted_operation(operation_output: OperationOutput):
                    if operation_output.deleted_at is None:
                        return True
                    else:
                        return False

                new_project_operation_output = list(
                    filter(filter_deleted_operation, project.operation_output)
                )

            # prepare project information
            project.files.clear()
            project.files.extend(new_project_files)

            project.operation_output.clear()
            project.operation_output.extend(new_project_operation_output)

        return projects
