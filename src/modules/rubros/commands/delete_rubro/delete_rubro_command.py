from pydantic import BaseModel


class DeleteRubroCommand(BaseModel):
    id: int
