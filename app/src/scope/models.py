from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database.base import Base


class ScopeType(Base):
    code: Mapped[str] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(unique=True)
    sort_order: Mapped[int] = mapped_column()
    objects: Mapped[list["Object"]] = relationship(
        back_populates="scope_type",
        lazy="raise",
        order_by="Object.sort_order",
        passive_deletes=True,
    )
