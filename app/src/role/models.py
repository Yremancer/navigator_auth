from datetime import datetime
from typing import Any, ClassVar

from sqlalchemy import Column, DateTime, ForeignKey, Table, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database.base import Base

role_permission = Table(
    "role_permission",
    Base.metadata,
    Column("role_id", ForeignKey("role.id", ondelete="CASCADE"), primary_key=True),
    Column(
        "permission_code",
        ForeignKey("permission.code", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Role(Base):
    __mapper_args__: ClassVar[dict[str, Any]] = {"eager_defaults": True}

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(unique=True)
    description: Mapped[str] = mapped_column(nullable=True)
    is_super: Mapped[bool] = mapped_column(nullable=False, default=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        server_default=func.now(),
        onupdate=func.now(),
    )
    permissions: Mapped[list["Permission"]] = relationship(
        secondary=role_permission,
        lazy="raise",
    )
