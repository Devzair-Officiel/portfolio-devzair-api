from fastapi import HTTPException, status

from app.repositories.category_repository import CategoryRepository
from app.schemas.category import CategoryCreate, CategoryResponse, CategoryUpdate


class CategoryService:
    def __init__(self, repository: CategoryRepository) -> None:
        self.repository = repository

    async def get_all(self) -> list[CategoryResponse]:
        cats = await self.repository.get_all()
        return [CategoryResponse.model_validate(c) for c in cats]

    async def create(self, data: CategoryCreate) -> CategoryResponse:
        cat = await self.repository.create(data.key, data.label_fr, data.label_en, data.accent)
        return CategoryResponse.model_validate(cat)

    async def update(self, category_id: int, data: CategoryUpdate) -> CategoryResponse:
        cat = await self.repository.update(
            category_id,
            **{k: v for k, v in data.model_dump().items() if v is not None},
        )
        if not cat:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
        return CategoryResponse.model_validate(cat)

    async def delete(self, category_id: int) -> None:
        deleted = await self.repository.delete(category_id)
        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    async def reorder(self, ordered_ids: list[int]) -> None:
        await self.repository.reorder(ordered_ids)
