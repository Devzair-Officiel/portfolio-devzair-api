from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.repositories.setting_repository import SettingRepository
from app.schemas.setting import SettingResponse, SettingUpsert
from app.services.setting_service import SettingService

router = APIRouter(prefix="/settings", tags=["settings"])


def get_setting_service(db: AsyncSession = Depends(get_db)) -> SettingService:
    return SettingService(SettingRepository(session=db))


@router.get("/", response_model=list[SettingResponse])
async def list_settings(
    service: SettingService = Depends(get_setting_service),
) -> list[SettingResponse]:
    return await service.get_all()


@router.put(
    "/{key}",
    response_model=SettingResponse,
    dependencies=[Depends(get_current_user)],
)
async def upsert_setting(
    key: str,
    data: SettingUpsert,
    service: SettingService = Depends(get_setting_service),
) -> SettingResponse:
    return await service.upsert(key, data)
