from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database.base import Base


class User(Base):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    external_id: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(nullable=False)
    full_name: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(nullable=False)
    last_login_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    assignments: Mapped[list["Assignment"]] = relationship(
        back_populates="user",
        foreign_keys="Assignment.user_id",
        lazy="raise",
    )
    grants: Mapped[list["Grant"]] = relationship(
        back_populates="user",
        foreign_keys="Grant.user_id",
        lazy="raise",
    )
