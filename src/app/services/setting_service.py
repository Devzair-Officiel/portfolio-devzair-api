from app.repositories.setting_repository import SettingRepository
from app.schemas.setting import SettingResponse, SettingUpsert


class SettingService:
    def __init__(self, repository: SettingRepository) -> None:
        self.repository = repository

    async def get_all(self) -> list[SettingResponse]:
        settings = await self.repository.get_all()
        return [SettingResponse.model_validate(s) for s in settings]

    async def upsert(self, key: str, data: SettingUpsert) -> SettingResponse:
        setting = await self.repository.upsert(key, data.value)
        return SettingResponse.model_validate(setting)
