from pydantic import BaseModel


class GetObraQuery(BaseModel):
    id: int
    usuario_id: int
