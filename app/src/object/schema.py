from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ObjectScopeTypeSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    code: str = Field(description="Код типа области", examples=["system", "program"])
    title: str = Field(
        description="Название типа области", examples=["Система", "Программа"]
    )


class ObjectSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    code: str = Field(
        description="Код объекта", examples=["program.profile", "system.program"]
    )
    title: str = Field(
        description="Название объекта", examples=["Профиль", "Программа"]
    )
    sort_order: int | None = Field(default=None, description="Порядок сортировки")
    scope_type: ObjectScopeTypeSchema = Field(description="В каком типе области обьект")
    created_at: datetime = Field(description="Дата созданий")


class ObjectAddSchema(BaseModel):
    code: str = Field(
        description="Код внутри типа области", examples=["profile", "program"]
    )
    title: str = Field(
        description="Название объекта", examples=["Профиль", "Программа"]
    )
    sort_order: int | None = Field(default=None, description="Порядок сортировки")
    scope_type_code: str = Field(description="Код типа области", examples=["program"])


class ObjectAddedSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    code: str = Field(
        description="Код объекта", examples=["program.profile", "system.program"]
    )
    title: str = Field(
        description="Название объекта", examples=["Профиль", "Программа"]
    )
    sort_order: int | None = Field(default=None, description="Порядок сортировки")
    scope_type_code: str = Field(description="Код типа области", examples=["program"])
    created_at: datetime = Field(description="Дата созданий")


class ObjectUpdateSchema(BaseModel):
    title: str = Field(
        description="Название объекта", examples=["Профиль", "Программа"]
    )
