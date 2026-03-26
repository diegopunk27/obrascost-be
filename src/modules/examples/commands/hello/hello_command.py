from pydantic import BaseModel, Field


class HelloCommand(BaseModel):
    name: str = Field(min_length=3, max_length=20)
