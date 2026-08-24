from pydantic import BaseModel, ConfigDict, Field
from src.setting import settings


class PermissionCheck(BaseModel):
    permission: str = Field(examples=["program.profile.update"])
    scope_id: int = Field(default=settings.SYSTEM_SCOPE_ID)


class CheckRequest(BaseModel):
    user_id: int | None = Field(
        default=None,
        description="Кого проверяем. Если не указан проверяется владелец токена",
    )
    checks: list[PermissionCheck] = Field(min_length=1, max_length=100)


class CheckResult(PermissionCheck):
    allowed: bool


class CheckResponse(BaseModel):
    user_id: int
    results: list[CheckResult]


class ScopeQuery(BaseModel):
    permission: str = Field(examples=["program.program.read"])
    scope_type: str | None = Field(
        default=None,
        description="Тип узлов в ответе. Если не указан берётся из кода права",
        examples=["profile"],
    )

    @property
    def target_scope_type(self) -> str:
        return self.scope_type or self.permission.split(".", 1)[0]


class ScopeListRequest(BaseModel):
    user_id: int | None = Field(
        default=None,
        description="Кого проверяем. Если не указан проверяется владелец токена",
    )
    queries: list[ScopeQuery] = Field(min_length=1, max_length=20)


class ScopeResult(BaseModel):
    permission: str
    scope_type: str
    scope_ids: list[int]


class ScopeListResponse(BaseModel):
    user_id: int
    results: list[ScopeResult]


class GrantedScope(BaseModel):
    scope_type: str = Field(examples=["program"])
    scope_ids: list[int] = Field(examples=[[17, 23]])


class GrantedPermission(BaseModel):
    permission: str = Field(examples=["program.program.update"])
    scopes: list[GrantedScope]


class UserRoleSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    scope_type_code: str
    scope_id: int
