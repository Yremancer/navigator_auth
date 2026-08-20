from typing import Annotated

from fastapi import Depends
from src.assignment.service import AssignmentService
from src.database.deps import SessionDep


def get_assignment_service(session: SessionDep) -> AssignmentService:
    return AssignmentService(session)


AssignmentServiceDep = Annotated[AssignmentService, Depends(get_assignment_service)]
