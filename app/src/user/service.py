from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from src.user.models import User


class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_external_id(self, external_id: str) -> User | None:
        return await self.session.scalar(
            select(User).where(User.external_id == external_id)
        )

    async def get_all(self) -> list[User]:
        return list((await self.session.scalars(select(User))).all())

    async def add(self, external_id: str, email: str, full_name: str) -> User:
        new_user = User(
            external_id=external_id,
            email=email,
            full_name=full_name,
            is_active=True,
            last_login_at=func.now(),
        )

        self.session.add(new_user)
        await self.session.flush()
        return new_user

    async def get_or_add(self, *, external_id: str, email: str, full_name: str) -> User:
        user = await self.get_by_external_id(external_id=external_id)

        if user is None:
            return await self.add(
                external_id=external_id, email=email, full_name=full_name
            )

        user.email = email
        user.full_name = full_name
        user.last_login_at = func.now()
        await self.session.flush()
        return user
