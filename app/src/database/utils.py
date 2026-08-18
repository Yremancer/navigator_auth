from sqlalchemy.ext.asyncio import AsyncSession
from src.database.base import Base
from src.exceptions import AppError


async def get_or_raise[M: Base](
    session: AsyncSession,
    model: type[M],
    pk: object,
    exc: type[AppError],
) -> M:
    obj = await session.get(model, pk)
    if obj is None:
        raise exc(code=pk)
    return obj
