from fastapi import APIRouter, status
from src.assignment.deps import AssignmentServiceDep
from src.assignment.schema import AssignmentAddSchema, AssignmentSchema
from src.authentication.deps import CurrentUser

router = APIRouter()


@router.get("/", status_code=status.HTTP_200_OK)
async def get_assignments(service: AssignmentServiceDep) -> list[AssignmentSchema]:
    return await service.get_all()


@router.post("/", status_code=status.HTTP_201_CREATED)
async def add_assignment(
    service: AssignmentServiceDep,
    payload: AssignmentAddSchema,
    current_user: CurrentUser,
) -> AssignmentSchema:
    return await service.add(payload=payload, granted_by=current_user)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_assignment(service: AssignmentServiceDep, id: int) -> None:
    await service.delete(id=id)
