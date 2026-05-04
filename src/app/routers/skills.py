from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.repositories.skill_repository import SkillRepository
from app.schemas.skill import SkillCreate, SkillResponse
from app.services.skill_service import SkillService

router = APIRouter(prefix="/skills", tags=["skills"])


def get_skill_service(db: AsyncSession = Depends(get_db)) -> SkillService:
    return SkillService(SkillRepository(session=db))


@router.get("/", response_model=list[SkillResponse])
async def list_skills(
    service: SkillService = Depends(get_skill_service),
) -> list[SkillResponse]:
    return await service.get_all()


@router.post(
    "/",
    response_model=SkillResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_user)],
)
async def create_skill(
    data: SkillCreate,
    service: SkillService = Depends(get_skill_service),
) -> SkillResponse:
    return await service.create(data)


@router.put(
    "/reorder",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_current_user)],
)
async def reorder_skills(
    ordered_ids: list[int],
    service: SkillService = Depends(get_skill_service),
) -> None:
    await service.reorder(ordered_ids)


@router.delete(
    "/{skill_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_current_user)],
)
async def delete_skill(
    skill_id: int,
    service: SkillService = Depends(get_skill_service),
) -> None:
    await service.delete(skill_id)
