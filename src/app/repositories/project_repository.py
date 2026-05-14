from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate


class ProjectRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_all(self, *, active_only: bool = False) -> list[Project]:
        query = select(Project)
        if active_only:
            query = query.where(Project.is_active == True)  # noqa: E712
        query = query.order_by(Project.order, Project.created_at.desc())
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_id(self, project_id: int) -> Project | None:
        result = await self.session.execute(
            select(Project).where(Project.id == project_id)
        )
        return result.scalar_one_or_none()

    async def create(self, data: ProjectCreate) -> Project:
        result = await self.session.execute(select(Project).order_by(Project.order.desc()))
        last = result.scalars().first()
        order = (last.order + 1) if last else 0
        payload = data.model_dump()
        payload["order"] = order
        project = Project(**payload)
        self.session.add(project)
        await self.session.commit()
        await self.session.refresh(project)
        return project

    async def update(self, project: Project, data: ProjectUpdate) -> Project:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(project, field, value)
        await self.session.commit()
        await self.session.refresh(project)
        return project

    async def reorder(self, ordered_ids: list[int]) -> None:
        for position, project_id in enumerate(ordered_ids):
            result = await self.session.execute(select(Project).where(Project.id == project_id))
            project = result.scalar_one_or_none()
            if project:
                project.order = position
        await self.session.commit()

    async def delete(self, project: Project) -> None:
        await self.session.delete(project)
        await self.session.commit()
