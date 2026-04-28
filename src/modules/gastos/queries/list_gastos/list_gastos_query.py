from pydantic import BaseModel


class ListGastosQuery(BaseModel):
    obra_id: int
