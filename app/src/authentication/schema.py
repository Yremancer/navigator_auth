from pydantic import BaseModel
from src.access.schema import GrantedPermission, UserRoleSchema


class MeSchema(BaseModel):
    id: int
    email: str
    full_name: str
    is_superuser: bool
    roles: list[UserRoleSchema]
    permissions: list[GrantedPermission]
