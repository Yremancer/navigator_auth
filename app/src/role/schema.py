from datetime import datetime

from pydantic import BaseModel, ConfigDict
from src.permission.schema import PermissionSchema


class RoleListSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None = None
    is_super: bool = False
    created_at: datetime
    updated_at: datetime | None = None


class RoleDetailSchema(RoleListSchema):
    permissions: list[PermissionSchema]


class RoleAddSchema(BaseModel):
    title: str
    description: str | None = None
    is_super: bool = False
    permissions: list[str]


class RoleUpdateSchema(BaseModel):
    title: str | None = None
    description: str | None = None
    is_super: bool | None = None
    permissions: list[str] | None = None
