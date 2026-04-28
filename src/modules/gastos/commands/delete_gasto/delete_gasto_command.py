from pydantic import BaseModel


class DeleteGastoCommand(BaseModel):
    id: int
    obra_id: int
