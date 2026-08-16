from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class PermissionObjectSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    code: str = Field(description="Код объекта", examples=["profile", "program"])
    title: str = Field(
        description="Название объекта", examples=["Профиль", "Программа"]
    )


class PermissionActionSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    code: str = Field(description="Код действия", examples=["read"])
    title: str = Field(description="Название действия", examples=["Чтение"])


class PermissionSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    code: str = Field(
        description="Код права", examples=["profile.read", "program.create"]
    )
    object: PermissionObjectSchema = Field(description="Объект права")
    action: PermissionActionSchema = Field(description="Дейтсвие права")
    created_at: datetime = Field(description="Дата созданий")


class PermissionAddSchema(BaseModel):
    object_code: str = Field(description="Код объекта", examples=["profile", "program"])
    action_code: str = Field(description="Код действия", examples=["read", "create"])


class PermissionAddedSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    code: str = Field(description="Код объекта", examples=["profile", "program"])
    object_code: str = Field(description="Код объекта", examples=["profile", "program"])
    action_code: str = Field(description="Код действия", examples=["read", "create"])
    created_at: datetime = Field(description="Дата созданий")
