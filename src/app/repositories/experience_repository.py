from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.experience import Experience


class ExperienceRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_all(self, active_only: bool = True) -> list[Experience]:
        q = select(Experience).order_by(Experience.order, Experience.id)
        if active_only:
            q = q.where(Experience.is_active == True)  # noqa: E712
        result = await self.session.execute(q)
        return list(result.scalars().all())

    async def get_by_id(self, experience_id: int) -> Experience | None:
        result = await self.session.execute(
            select(Experience).where(Experience.id == experience_id)
        )
        return result.scalar_one_or_none()

    async def create(self, **kwargs: object) -> Experience:
        result = await self.session.execute(
            select(Experience).order_by(Experience.order.desc())
        )
        last = result.scalars().first()
        order = (last.order + 1) if last else 0
        exp = Experience(order=order, **kwargs)
        self.session.add(exp)
        await self.session.commit()
        await self.session.refresh(exp)
        return exp

    async def update(self, experience_id: int, **kwargs: object) -> Experience | None:
        exp = await self.get_by_id(experience_id)
        if not exp:
            return None
        for field, value in kwargs.items():
            if value is not None:
                setattr(exp, field, value)
        await self.session.commit()
        await self.session.refresh(exp)
        return exp

    async def delete(self, experience_id: int) -> bool:
        exp = await self.get_by_id(experience_id)
        if not exp:
            return False
        await self.session.delete(exp)
        await self.session.commit()
        return True
