from pydantic import BaseModel


class SkillResponse(BaseModel):
    id: int
    name: str
    category: str
    order: int

    model_config = {"from_attributes": True}


class SkillCreate(BaseModel):
    name: str
    category: str
