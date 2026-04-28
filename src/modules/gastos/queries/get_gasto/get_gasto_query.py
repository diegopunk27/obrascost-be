from pydantic import BaseModel


class GetGastoQuery(BaseModel):
    id: int
    obra_id: int
