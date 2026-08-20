from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database.base import Base


class Assignment(Base):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"))
    role_id: Mapped[int] = mapped_column(ForeignKey("role.id", ondelete="CASCADE"))
    scope_type_code: Mapped[str] = mapped_column(
        ForeignKey("scopetype.code", ondelete="CASCADE")
    )
    scope_id: Mapped[int]
    granted_by_id: Mapped[int | None] = mapped_column(
        ForeignKey("user.id", ondelete="SET NULL")
    )

    user: Mapped["User"] = relationship(
        back_populates="assignments",
        foreign_keys=[user_id],
        lazy="raise",
    )
    granted_by: Mapped["User | None"] = relationship(
        foreign_keys=[granted_by_id], lazy="raise"
    )
    role: Mapped["Role"] = relationship(lazy="raise")
    scope_type: Mapped["ScopeType"] = relationship(lazy="raise")
