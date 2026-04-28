from pydantic import BaseModel


class ListRubrosQuery(BaseModel):
    solo_activos: bool = True
