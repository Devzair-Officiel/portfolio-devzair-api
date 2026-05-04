from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.skill import Skill


class SkillRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_all(self) -> list[Skill]:
        result = await self.session.execute(select(Skill).order_by(Skill.category, Skill.order, Skill.id))
        return list(result.scalars().all())

    async def create(self, name: str, category: str) -> Skill:
        result = await self.session.execute(
            select(Skill).where(Skill.category == category).order_by(Skill.order.desc())
        )
        last = result.scalars().first()
        order = (last.order + 1) if last else 0
        skill = Skill(name=name, category=category, order=order)
        self.session.add(skill)
        await self.session.commit()
        await self.session.refresh(skill)
        return skill

    async def reorder(self, ordered_ids: list[int]) -> None:
        for position, skill_id in enumerate(ordered_ids):
            result = await self.session.execute(select(Skill).where(Skill.id == skill_id))
            skill = result.scalar_one_or_none()
            if skill:
                skill.order = position
        await self.session.commit()

    async def delete(self, skill_id: int) -> bool:
        result = await self.session.execute(select(Skill).where(Skill.id == skill_id))
        skill = result.scalar_one_or_none()
        if not skill:
            return False
        await self.session.delete(skill)
        await self.session.commit()
        return True
