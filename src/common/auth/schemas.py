from pydantic import BaseModel, ConfigDict, Field


class UserSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    email: str
    role_id: int
    role_name: str
    permissions: list[str] | None = None


class TokenPayload(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    sub: str
    email: str
    role_id: int = Field(validation_alias="roleId")
    role_name: str = Field(validation_alias="roleName")
    permissions: list[str] | None = None
