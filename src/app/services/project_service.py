from fastapi import HTTPException, status

from app.repositories.project_repository import ProjectRepository
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate


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
        updated = await self.repository.update(project, data)
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
        await self.repository.delete(project)
