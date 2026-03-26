from pydantic import BaseModel, Field


class CreateLogCommand(BaseModel):
    message: str
    stack_trace: str = Field(default="")
