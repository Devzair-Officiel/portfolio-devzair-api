from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category


class CategoryRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_all(self) -> list[Category]:
        result = await self.session.execute(select(Category).order_by(Category.order, Category.id))
        return list(result.scalars().all())

    async def get_by_id(self, category_id: int) -> Category | None:
        result = await self.session.execute(select(Category).where(Category.id == category_id))
        return result.scalar_one_or_none()

    async def create(self, key: str, label_fr: str, label_en: str, accent: str) -> Category:
        result = await self.session.execute(select(Category).order_by(Category.order.desc()))
        last = result.scalars().first()
        order = (last.order + 1) if last else 0
        cat = Category(key=key, label_fr=label_fr, label_en=label_en, accent=accent, order=order)
        self.session.add(cat)
        await self.session.commit()
        await self.session.refresh(cat)
        return cat

    async def update(self, category_id: int, **kwargs: str) -> Category | None:
        cat = await self.get_by_id(category_id)
        if not cat:
            return None
        for field, value in kwargs.items():
            if value is not None:
                setattr(cat, field, value)
        await self.session.commit()
        await self.session.refresh(cat)
        return cat

    async def delete(self, category_id: int) -> bool:
        cat = await self.get_by_id(category_id)
        if not cat:
            return False
        await self.session.delete(cat)
        await self.session.commit()
        return True

    async def reorder(self, ordered_ids: list[int]) -> None:
        for position, cat_id in enumerate(ordered_ids):
            cat = await self.get_by_id(cat_id)
            if cat:
                cat.order = position
        await self.session.commit()
