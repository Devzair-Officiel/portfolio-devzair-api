from fastapi import HTTPException, status

from app.repositories.experience_repository import ExperienceRepository
from app.schemas.experience import ExperienceCreate, ExperienceResponse, ExperienceUpdate


class ExperienceService:
    def __init__(self, repository: ExperienceRepository) -> None:
        self.repository = repository

    async def get_all(self, active_only: bool = True) -> list[ExperienceResponse]:
        exps = await self.repository.get_all(active_only=active_only)
        return [ExperienceResponse.model_validate(e) for e in exps]

    async def get_experience(self, experience_id: int) -> ExperienceResponse:
        exp = await self.repository.get_by_id(experience_id)
        if not exp:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Experience not found")
        return ExperienceResponse.model_validate(exp)

    async def create(self, data: ExperienceCreate) -> ExperienceResponse:
        exp = await self.repository.create(**data.model_dump())
        return ExperienceResponse.model_validate(exp)

    async def update(self, experience_id: int, data: ExperienceUpdate) -> ExperienceResponse:
        exp = await self.repository.update(
            experience_id,
            **{k: v for k, v in data.model_dump().items() if v is not None},
        )
        if not exp:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Experience not found")
        return ExperienceResponse.model_validate(exp)

    async def delete(self, experience_id: int) -> None:
        deleted = await self.repository.delete(experience_id)
        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Experience not found")
