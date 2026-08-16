from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database.base import Base


class Object(Base):
    code: Mapped[str] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(unique=True)
    sort_order: Mapped[int]
    scope_type_code: Mapped[str] = mapped_column(
        ForeignKey("scopetype.code", ondelete="CASCADE")
    )
    scope_type: Mapped["ScopeType"] = relationship(
        back_populates="objects", lazy="raise"
    )
