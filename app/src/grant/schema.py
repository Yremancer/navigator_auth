from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field
from src.scope.schema import ScopeTypeSchema
from src.setting import settings
from src.user.schema import UserSchema


class GrantSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(description="ID назначения")
    user: UserSchema = Field(description="Пользователь, которому назначили право")
    permission_code: str = Field(description="Код назначаемого права")
    scope_type: ScopeTypeSchema = Field(description="Тип области назначения")
    scope_id: int = Field(description="ID обьекта назначения")
    granted_by: UserSchema = Field(description="Пользователь, который назначил право")
    created_at: datetime = Field(description="Дата созданий")


class GrantAddSchema(BaseModel):
    user_id: int = Field(description="ID пользователя, которому назначили роль")
    permission_code: str = Field(description="Код назначаемого права")
    scope_type_code: str = Field(description="Код типа области назначения")
    scope_id: int | None= Field(
        default=settings.SYSTEM_SCOPE_ID,
        description="ID обьекта назначения. Система = 0",
    )
