from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.repositories.category_repository import CategoryRepository
from app.schemas.category import CategoryCreate, CategoryResponse, CategoryUpdate
from app.services.category_service import CategoryService

router = APIRouter(prefix="/categories", tags=["categories"])


def get_category_service(db: AsyncSession = Depends(get_db)) -> CategoryService:
    return CategoryService(CategoryRepository(session=db))


@router.get("/", response_model=list[CategoryResponse])
async def list_categories(
    service: CategoryService = Depends(get_category_service),
) -> list[CategoryResponse]:
    return await service.get_all()


@router.post(
    "/",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_user)],
)
async def create_category(
    data: CategoryCreate,
    service: CategoryService = Depends(get_category_service),
) -> CategoryResponse:
    return await service.create(data)


@router.patch(
    "/{category_id}",
    response_model=CategoryResponse,
    dependencies=[Depends(get_current_user)],
)
async def update_category(
    category_id: int,
    data: CategoryUpdate,
    service: CategoryService = Depends(get_category_service),
) -> CategoryResponse:
    return await service.update(category_id, data)


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_current_user)],
)
async def delete_category(
    category_id: int,
    service: CategoryService = Depends(get_category_service),
) -> None:
    await service.delete(category_id)


@router.put(
    "/reorder",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_current_user)],
)
async def reorder_categories(
    ordered_ids: list[int],
    service: CategoryService = Depends(get_category_service),
) -> None:
    await service.reorder(ordered_ids)
