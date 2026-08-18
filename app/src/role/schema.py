from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field
from src.permission.schema import PermissionSchema


class RoleListSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(description="ID роли")
    title: str = Field(description="Название роли", examples=["РОП", "Профильный РОП"])
    description: str | None = Field(description="Описание роли")
    updated_at: datetime | None = Field(description="Дата последнего обновления")
    created_at: datetime = Field(description="Дата созданий")


class RoleDetailSchema(RoleListSchema):
    permissions: list[PermissionSchema] = Field(
        description=("Коды прав роли"), examples=["program.profile.read"]
    )


class RoleAddSchema(BaseModel):
    title: str = Field(description="Название роли", examples=["РОП", "Профильный РОП"])
    description: str | None = Field(description="Описание роли")
    permissions: list[str] = Field(
        description=("Коды прав роли"), examples=["program.profile.read"]
    )


class RolePermissionSchema(BaseModel):
    code: str = Field(description="Код объекта", examples=["profile", "program"])
    object_code: str = Field(description="Код объекта", examples=["profile", "program"])
    action_code: str = Field(description="Код действия", examples=["read", "create"])
    created_at: datetime = Field(description="Дата созданий")


class RoleAddedSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(description="ID роли")
    title: str = Field(description="Название роли", examples=["РОП", "Профильный РОП"])
    description: str | None = Field(description="Описание роли")
    updated_at: datetime | None = Field(description="Дата последнего обновления")
    created_at: datetime = Field(description="Дата созданий")
    permissions: list[RolePermissionSchema] = Field(
        description=("Коды прав роли"), examples=["program.profile.read"]
    )


class RoleUpdateSchema(RoleAddSchema):
    pass


class RoleUpdatedSchema(RoleAddedSchema):
    pass
