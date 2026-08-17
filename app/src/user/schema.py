from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class UserSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(description="ID пользователя")
    email: str = Field(description="Почта пользователя")
    full_name: str = Field(description="Полное имя пользователя")
    is_active: bool = Field(description="Активен ли пользователь")
    last_login_at: datetime | None = Field(description="Дата последнего входа")
    created_at: datetime = Field(description="Дата созданий")
