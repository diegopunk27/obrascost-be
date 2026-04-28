from pydantic import BaseModel, EmailStr, Field


class LoginCommand(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
