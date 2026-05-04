from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.skill import Skill


class SkillRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_all(self) -> list[Skill]:
        result = await self.session.execute(select(Skill).order_by(Skill.category, Skill.id))
        return list(result.scalars().all())

    async def create(self, name: str, category: str) -> Skill:
        skill = Skill(name=name, category=category)
        self.session.add(skill)
        await self.session.commit()
        await self.session.refresh(skill)
        return skill

    async def delete(self, skill_id: int) -> bool:
        result = await self.session.execute(select(Skill).where(Skill.id == skill_id))
        skill = result.scalar_one_or_none()
        if not skill:
            return False
        await self.session.delete(skill)
        await self.session.commit()
        return True
