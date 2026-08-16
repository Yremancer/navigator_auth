from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database.base import Base


class Permission(Base):
    code: Mapped[str] = mapped_column(primary_key=True)
    object_code: Mapped[str] = mapped_column(
        ForeignKey("object.code", ondelete="CASCADE")
    )
    action_code: Mapped[str] = mapped_column(
        ForeignKey("action.code", ondelete="CASCADE")
    )
    object: Mapped["Object"] = relationship(back_populates="permissions",lazy="raise")
    action: Mapped["Action"] = relationship(lazy="raise")
