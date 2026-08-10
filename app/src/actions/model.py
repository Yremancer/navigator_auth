from sqlalchemy.orm import Mapped, mapped_column
from src.database.base import Base


class Action(Base):
    code: Mapped[str] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(unique=True, nullable=False)
    sort_order: Mapped[int] = mapped_column(nullable=False, default=0)
