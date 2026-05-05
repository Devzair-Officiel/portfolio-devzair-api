from sqlalchemy import Boolean, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class Experience(Base, TimestampMixin):
    __tablename__ = "experiences"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    role_fr: Mapped[str] = mapped_column(String(200), nullable=False)
    role_en: Mapped[str] = mapped_column(String(200), nullable=False)
    company: Mapped[str] = mapped_column(String(200), nullable=False)
    period: Mapped[str] = mapped_column(String(100), nullable=False)
    description_fr: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    description_en: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
