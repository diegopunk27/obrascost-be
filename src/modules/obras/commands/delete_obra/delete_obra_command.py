from pydantic import BaseModel


class DeleteObraCommand(BaseModel):
    id: int
    usuario_id: int
