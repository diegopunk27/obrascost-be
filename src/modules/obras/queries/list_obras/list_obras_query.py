from pydantic import BaseModel


class ListObrasQuery(BaseModel):
    usuario_id: int
