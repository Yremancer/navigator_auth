from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


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
