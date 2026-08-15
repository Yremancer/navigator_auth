from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ActionSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    code: str = Field(description="Код действия", examples=["read"])
    title: str = Field(description="Название действия", examples=["Чтение"])
    sort_order: int | None = Field(default=None, description="Порядок сортировки")
    created_at: datetime = Field(description="Дата созданий")


class ActionAddSchema(BaseModel):
    code: str = Field(description="Код действия", examples=["read"])
    title: str = Field(description="Название действия", examples=["Чтение"])
    sort_order: int | None = Field(default=None, description="Порядок сортировки")


class ActionUpdateSchema(BaseModel):
    title: str = Field(description="Название действия", examples=["Чтение"])
