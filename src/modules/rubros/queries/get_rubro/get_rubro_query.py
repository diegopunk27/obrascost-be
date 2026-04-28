from pydantic import BaseModel


class GetRubroQuery(BaseModel):
    id: int
