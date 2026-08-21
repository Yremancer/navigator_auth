from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from src.assignment.exceptions import AssignmentNotFoundError
from src.assignment.models import Assignment
from src.assignment.schema import AssignmentAddSchema
from src.database.utils import get_or_raise
from src.role.exceptions import RoleNotFoundError
from src.role.models import Role
from src.scope.exceptions import ScopeNotFoundError, ScopeTypeNotFoundError
from src.scope.models import Scope, ScopeType
from src.user.exceptions import UserNotFoundError
from src.user.models import User


class AssignmentService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self) -> list[Assignment]:
        return list(
            (
                await self.session.scalars(
                    select(Assignment).options(
                        joinedload(Assignment.user),
                        joinedload(Assignment.scope_type),
                        joinedload(Assignment.role),
                        joinedload(Assignment.granted_by),
                    )
                )
            ).all()
        )

    async def add(self, payload: AssignmentAddSchema, granted_by: User) -> Assignment:
        user = await get_or_raise(
            session=self.session, model=User, pk=payload.user_id, exc=UserNotFoundError
        )
        scope_type = await get_or_raise(
            session=self.session,
            model=ScopeType,
            pk=payload.scope_type_code,
            exc=ScopeTypeNotFoundError,
        )
        role = await get_or_raise(
            session=self.session,
            model=Role,
            pk=payload.role_id,
            exc=RoleNotFoundError,
        )
        scope = await get_or_raise(
            session=self.session,
            model=Scope,
            pk=(payload.scope_type_code, payload.scope_id),
            exc=ScopeNotFoundError,
        )

        new_assignment = Assignment(**payload.model_dump(exclude_none=True))
        new_assignment.user = user
        new_assignment.role = role
        new_assignment.scope_type = scope_type
        new_assignment.granted_by = granted_by

        self.session.add(new_assignment)
        await self.session.flush()
        return new_assignment

    async def delete(self, id: int) -> None:
        assignment = await get_or_raise(
            session=self.session,
            model=Assignment,
            pk=id,
            exc=AssignmentNotFoundError,
        )

        await self.session.delete(assignment)

        await self.session.flush()
