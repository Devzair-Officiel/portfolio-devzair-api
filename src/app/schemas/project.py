from datetime import datetime

from pydantic import BaseModel, HttpUrl


class ProjectBase(BaseModel):
    title: str
    description: str
    stack: list[str]
    github_url: HttpUrl | None = None
    live_url: HttpUrl | None = None
    is_active: bool = True


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    stack: list[str] | None = None
    github_url: HttpUrl | None = None
    live_url: HttpUrl | None = None
    is_active: bool | None = None


class ProjectResponse(ProjectBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
