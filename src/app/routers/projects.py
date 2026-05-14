from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.repositories.project_repository import ProjectRepository
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate
from app.services.project_service import ProjectService

router = APIRouter(prefix="/projects", tags=["projects"])


def get_project_service(db: AsyncSession = Depends(get_db)) -> ProjectService:
    return ProjectService(ProjectRepository(session=db))


@router.get("/", response_model=list[ProjectResponse])
async def list_projects(
    active_only: bool = True,
    service: ProjectService = Depends(get_project_service),
) -> list[ProjectResponse]:
    return await service.get_all_projects(active_only=active_only)


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    service: ProjectService = Depends(get_project_service),
) -> ProjectResponse:
    return await service.get_project(project_id)


@router.post(
    "/",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_user)],
)
async def create_project(
    data: ProjectCreate,
    service: ProjectService = Depends(get_project_service),
) -> ProjectResponse:
    return await service.create_project(data)


@router.patch(
    "/{project_id}",
    response_model=ProjectResponse,
    dependencies=[Depends(get_current_user)],
)
async def update_project(
    project_id: int,
    data: ProjectUpdate,
    service: ProjectService = Depends(get_project_service),
) -> ProjectResponse:
    return await service.update_project(project_id, data)


@router.put(
    "/reorder",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_current_user)],
)
async def reorder_projects(
    ordered_ids: list[int],
    service: ProjectService = Depends(get_project_service),
) -> None:
    await service.reorder_projects(ordered_ids)


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_current_user)],
)
async def delete_project(
    project_id: int,
    service: ProjectService = Depends(get_project_service),
) -> None:
    await service.delete_project(project_id)
