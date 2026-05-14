from pathlib import Path

from fastapi import HTTPException, status

from app.repositories.project_repository import ProjectRepository
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate

UPLOAD_DIR = Path("/app/uploads")


def _delete_upload(image_url: str | None) -> None:
    if not image_url:
        return
    filename = Path(image_url).name
    filepath = UPLOAD_DIR / filename
    if filepath.exists() and filepath.is_file():
        filepath.unlink()


class ProjectService:
    def __init__(self, repository: ProjectRepository) -> None:
        self.repository = repository

    async def get_all_projects(self, *, active_only: bool = True) -> list[ProjectResponse]:
        projects = await self.repository.get_all(active_only=active_only)
        return [ProjectResponse.model_validate(p) for p in projects]

    async def get_project(self, project_id: int) -> ProjectResponse:
        project = await self.repository.get_by_id(project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Projet {project_id} introuvable",
            )
        return ProjectResponse.model_validate(project)

    async def create_project(self, data: ProjectCreate) -> ProjectResponse:
        project = await self.repository.create(data)
        return ProjectResponse.model_validate(project)

    async def update_project(self, project_id: int, data: ProjectUpdate) -> ProjectResponse:
        project = await self.repository.get_by_id(project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Projet {project_id} introuvable",
            )
        old_image = project.image_url
        updated = await self.repository.update(project, data)
        # Si l'image a changé, supprimer l'ancienne du disque
        if data.image_url is not None and old_image != data.image_url:
            _delete_upload(old_image)
        return ProjectResponse.model_validate(updated)

    async def reorder_projects(self, ordered_ids: list[int]) -> None:
        await self.repository.reorder(ordered_ids)

    async def delete_project(self, project_id: int) -> None:
        project = await self.repository.get_by_id(project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Projet {project_id} introuvable",
            )
        image_url = project.image_url
        await self.repository.delete(project)
        _delete_upload(image_url)
