from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.repositories.experience_repository import ExperienceRepository
from app.schemas.experience import ExperienceCreate, ExperienceResponse, ExperienceUpdate
from app.services.experience_service import ExperienceService

router = APIRouter(prefix="/experiences", tags=["experiences"])


def get_service(db: AsyncSession = Depends(get_db)) -> ExperienceService:
    return ExperienceService(ExperienceRepository(session=db))


@router.get("/", response_model=list[ExperienceResponse])
async def list_experiences(
    active_only: bool = True,
    service: ExperienceService = Depends(get_service),
) -> list[ExperienceResponse]:
    return await service.get_all(active_only=active_only)


@router.post(
    "/",
    response_model=ExperienceResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_user)],
)
async def create_experience(
    data: ExperienceCreate,
    service: ExperienceService = Depends(get_service),
) -> ExperienceResponse:
    return await service.create(data)


@router.patch(
    "/{experience_id}",
    response_model=ExperienceResponse,
    dependencies=[Depends(get_current_user)],
)
async def update_experience(
    experience_id: int,
    data: ExperienceUpdate,
    service: ExperienceService = Depends(get_service),
) -> ExperienceResponse:
    return await service.update(experience_id, data)


@router.delete(
    "/{experience_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_current_user)],
)
async def delete_experience(
    experience_id: int,
    service: ExperienceService = Depends(get_service),
) -> None:
    await service.delete(experience_id)
