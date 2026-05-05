from pydantic import BaseModel


class ExperienceResponse(BaseModel):
    id: int
    role_fr: str
    role_en: str
    company: str
    period: str
    description_fr: list[str]
    description_en: list[str]
    order: int
    is_active: bool

    model_config = {"from_attributes": True}


class ExperienceCreate(BaseModel):
    role_fr: str
    role_en: str
    company: str
    period: str
    description_fr: list[str] = []
    description_en: list[str] = []
    is_active: bool = True


class ExperienceUpdate(BaseModel):
    role_fr: str | None = None
    role_en: str | None = None
    company: str | None = None
    period: str | None = None
    description_fr: list[str] | None = None
    description_en: list[str] | None = None
    order: int | None = None
    is_active: bool | None = None
