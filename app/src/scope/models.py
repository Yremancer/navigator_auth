from sqlalchemy import ForeignKey, ForeignKeyConstraint
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


class Scope(Base):
    __table_args__ = (
        ForeignKeyConstraint(
            ["parent_type", "parent_id"],
            ["scope.scope_type", "scope.scope_id"],
            ondelete="CASCADE",
        ),
    )

    scope_type: Mapped[str] = mapped_column(
        ForeignKey("scopetype.code"), primary_key=True
    )
    scope_id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(nullable=True)
    parent_type: Mapped[str | None]
    parent_id: Mapped[int | None]

    parent: Mapped["Scope | None"] = relationship(
        back_populates="children",
        remote_side="[Scope.scope_type, Scope.scope_id]",
        lazy="raise",
    )
    children: Mapped[list["Scope"]] = relationship(
        back_populates="parent",
        passive_deletes=True,
        lazy="raise",
    )
