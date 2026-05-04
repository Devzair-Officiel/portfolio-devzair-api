from fastapi import HTTPException, status

from app.repositories.skill_repository import SkillRepository
from app.schemas.skill import SkillCreate, SkillResponse


class SkillService:
    def __init__(self, repository: SkillRepository) -> None:
        self.repository = repository

    async def get_all(self) -> list[SkillResponse]:
        skills = await self.repository.get_all()
        return [SkillResponse.model_validate(s) for s in skills]

    async def create(self, data: SkillCreate) -> SkillResponse:
        skill = await self.repository.create(data.name, data.category)
        return SkillResponse.model_validate(skill)

    async def delete(self, skill_id: int) -> None:
        deleted = await self.repository.delete(skill_id)
        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Skill not found")
