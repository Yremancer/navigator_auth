from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field
from src.setting import settings


class ScopeTypeSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    code: str = Field(description="Код типа области", examples=["system", "program"])
    title: str = Field(
        description="Название типа области", examples=["Система", "Программа"]
    )
    sort_order: int | None = Field(default=None, description="Порядок сортировки")
    created_at: datetime = Field(description="Дата созданий")


class ScopeTypeAddSchema(BaseModel):
    code: str = Field(description="Код типа области", examples=["system", "program"])
    title: str = Field(
        description="Название типа области", examples=["Система", "Программа"]
    )
    sort_order: int | None = Field(default=None, description="Порядок сортировки")


class ScopeTypeUpdateSchema(BaseModel):
    title: str = Field(
        description="Название типа области", examples=["Система", "Программа"]
    )


class ActionTreeSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    code: str = Field(description="Код действия", examples=["read"])
    title: str = Field(description="Название действия", examples=["Чтение"])


class PermissionTreeSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    code: str
    action: ActionTreeSchema = Field()


class ObjectTreeSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    code: str
    title: str
    permissions: list[PermissionTreeSchema]


class ScopeTypeTreeSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    code: str
    title: str
    objects: list[ObjectTreeSchema]


class ScopeSchema(BaseModel):
    scope_type: str = Field(description="Код типа области", examples=["program"])
    scope_id: int = Field(description="ID области")
    title: str | None = Field(
        description="Название области",
        examples=["Разработка и управление цифровых продуктов"],
    )
    parent_type: str | None = Field(
        description="Код типа области", examples=["program"]
    )
    parent_id: int | None = Field(description="ID области")
    created_at: datetime = Field(description="Дата созданий")


class ScopeAddSchema(BaseModel):
    scope_type: str = Field(description="Код типа области", examples=["program"])
    scope_id: int = Field(description="ID области")
    title: str | None = Field(
        description="Название области",
        examples=["Разработка и управление цифровых продуктов"],
    )
    parent_type: str | None = Field(
        description="Код типа области", examples=["program"]
    )
    parent_id: int | None = Field(
        default=settings.SYSTEM_SCOPE_ID, description="ID области"
    )
