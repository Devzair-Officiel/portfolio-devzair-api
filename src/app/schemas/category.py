from pydantic import BaseModel


class CategoryResponse(BaseModel):
    id: int
    key: str
    label_fr: str
    label_en: str
    accent: str
    order: int

    model_config = {"from_attributes": True}


class CategoryCreate(BaseModel):
    key: str
    label_fr: str
    label_en: str
    accent: str = "#818cf8"


class CategoryUpdate(BaseModel):
    label_fr: str | None = None
    label_en: str | None = None
    accent: str | None = None
