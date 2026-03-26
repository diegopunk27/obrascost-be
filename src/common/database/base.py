from sqlmodel import Field, SQLModel


class MasterModel(SQLModel, table=True):
    """Reference base model (catalog-style), similar to NestJS MasterEntity."""

    id: int = Field(primary_key=True)
    description: str
